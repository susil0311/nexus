"""Matches review API routes."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    ActivityMatch,
    ActualProgress,
    ExtractedEvent,
    MatchStatus,
    ProcessingStatus,
    ScheduleNode,
    User,
)
from app.schemas.schemas import (
    BulkApproveRequest,
    MatchApproveRequest,
    MatchRejectRequest,
    MatchResponse,
    PaginatedResponse,
)
from app.services.audit_service import log_action

router = APIRouter(prefix="/matches", tags=["matches"])


# ---------------------------------------------------------------------------
# GET /api/matches/review-queue
# ---------------------------------------------------------------------------

@router.get("/review-queue", response_model=PaginatedResponse[MatchResponse])
async def review_queue(
    project_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MatchResponse]:
    """Return paginated list of matches that need human review."""
    query = (
        select(ActivityMatch)
        .options(
            selectinload(ActivityMatch.extracted_event),
            selectinload(ActivityMatch.schedule_node),
        )
        .order_by(ActivityMatch.created_at.desc())
    )

    if status_filter:
        try:
            ms = MatchStatus(status_filter)
        except ValueError:
            ms = MatchStatus.needs_review
        query = query.where(ActivityMatch.status == ms)
    else:
        query = query.where(ActivityMatch.status == MatchStatus.needs_review)

    if project_id:
        # Join through extracted_event → field_submission.project_id is expensive;
        # easier: join ExtractedEvent
        query = query.join(
            ExtractedEvent, ActivityMatch.extracted_event_id == ExtractedEvent.id
        ).where(ExtractedEvent.project_id == project_id)

    # Count total
    count_query = query.with_only_columns(ActivityMatch.id)  # type: ignore[arg-type]
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    # Paginate
    offset = (page - 1) * page_size
    paginated = query.offset(offset).limit(page_size)
    result = await db.execute(paginated)
    items = [MatchResponse.model_validate(m) for m in result.scalars().all()]

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


# ---------------------------------------------------------------------------
# PATCH /api/matches/{id}/approve
# ---------------------------------------------------------------------------

@router.patch("/{match_id}/approve", response_model=MatchResponse)
async def approve_match(
    request: Request,
    match_id: uuid.UUID,
    payload: MatchApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchResponse:
    """Approve a match – sets status to auto_accepted and creates ActualProgress."""
    result = await db.execute(
        select(ActivityMatch)
        .where(ActivityMatch.id == match_id)
        .options(selectinload(ActivityMatch.extracted_event))
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    now = datetime.now(timezone.utc)
    match.status = MatchStatus.auto_accepted
    match.reviewed_by = current_user.id
    match.reviewed_at = now

    # Create / update ActualProgress
    if match.schedule_node_id and match.extracted_event:
        event = match.extracted_event
        ap = ActualProgress(
            project_id=event.project_id,
            schedule_node_id=match.schedule_node_id,
            match_id=match.id,
            actual_start=event.extracted_start,
            actual_finish=event.extracted_finish,
            progress_pct=float(event.progress_pct) if event.progress_pct else 0.0,
            is_complete=(float(event.progress_pct or 0) >= 100.0),
            confidence_score=float(match.match_score) if match.match_score else None,
            source_type="field_submission",
        )
        db.add(ap)

    await db.flush()
    await log_action(
        db=db,
        user_id=current_user.id,
        action="approve_match",
        entity="activity_match",
        entity_id=match.id,
        old_value={"status": "needs_review"},
        new_value={"status": "auto_accepted", "note": payload.note},
        ip=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(match)
    return MatchResponse.model_validate(match)


# ---------------------------------------------------------------------------
# PATCH /api/matches/{id}/reject
# ---------------------------------------------------------------------------

@router.patch("/{match_id}/reject", response_model=MatchResponse)
async def reject_match(
    request: Request,
    match_id: uuid.UUID,
    payload: MatchRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchResponse:
    """Reject a match – sets status to rejected."""
    result = await db.execute(select(ActivityMatch).where(ActivityMatch.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    now = datetime.now(timezone.utc)
    match.status = MatchStatus.rejected
    match.reviewed_by = current_user.id
    match.reviewed_at = now

    await log_action(
        db=db,
        user_id=current_user.id,
        action="reject_match",
        entity="activity_match",
        entity_id=match.id,
        old_value={"status": "needs_review"},
        new_value={"status": "rejected", "reason": payload.reason},
        ip=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(match)
    return MatchResponse.model_validate(match)


# ---------------------------------------------------------------------------
# POST /api/matches/bulk-approve
# ---------------------------------------------------------------------------

@router.post("/bulk-approve", response_model=dict)
async def bulk_approve(
    request: Request,
    payload: BulkApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Approve multiple matches at once."""
    now = datetime.now(timezone.utc)
    approved_count = 0

    result = await db.execute(
        select(ActivityMatch)
        .where(ActivityMatch.id.in_(payload.match_ids))
        .options(selectinload(ActivityMatch.extracted_event))
    )
    matches = result.scalars().all()

    for match in matches:
        if match.status not in (MatchStatus.auto_accepted, MatchStatus.rejected):
            match.status = MatchStatus.auto_accepted
            match.reviewed_by = current_user.id
            match.reviewed_at = now

            if match.schedule_node_id and match.extracted_event:
                event = match.extracted_event
                ap = ActualProgress(
                    project_id=event.project_id,
                    schedule_node_id=match.schedule_node_id,
                    match_id=match.id,
                    actual_start=event.extracted_start,
                    actual_finish=event.extracted_finish,
                    progress_pct=float(event.progress_pct) if event.progress_pct else 0.0,
                    is_complete=(float(event.progress_pct or 0) >= 100.0),
                    confidence_score=float(match.match_score) if match.match_score else None,
                    source_type="field_submission",
                )
                db.add(ap)
            approved_count += 1

    await db.commit()
    return {"approved": approved_count, "total_requested": len(payload.match_ids)}
