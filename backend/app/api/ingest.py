"""Ingest API routes – text, file, voice submissions."""
import os
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    ActivityMatch,
    ExtractedEvent,
    FieldSubmission,
    ProcessingStatus,
    SubmissionType,
    User,
)
from app.schemas.schemas import (
    ExtractedEventResponse,
    MatchResponse,
    SubmissionResponse,
    SubmissionStatus,
    TextIngestionRequest,
)

router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# POST /api/ingest/text
# ---------------------------------------------------------------------------

@router.post("/text", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_text(
    payload: TextIngestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """Accept free-text field report, persist, and queue for AI extraction."""
    submission = FieldSubmission(
        project_id=payload.project_id,
        submitted_by=current_user.id,
        submission_type=SubmissionType.text,
        raw_content=payload.content,
        discipline=payload.discipline,
        submission_date=payload.submission_date or date.today(),
        processing_status=ProcessingStatus.pending,
    )
    db.add(submission)
    await db.flush()
    sub_id = submission.id
    await db.commit()

    # Trigger Celery task (fire and forget – import here to avoid circular)
    try:
        from app.tasks.ingest_tasks import process_text_submission
        process_text_submission.delay(str(sub_id))
    except Exception:
        # Celery may not be running in test/dev – submission still persisted
        pass

    await db.refresh(submission)
    return SubmissionResponse.model_validate(submission)


# ---------------------------------------------------------------------------
# POST /api/ingest/file
# ---------------------------------------------------------------------------

@router.post("/file", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_file(
    project_id: uuid.UUID = Form(...),
    discipline: str = Form(None),
    submission_date: str = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """Accept Excel / PDF / DPR file upload, persist, and queue for processing."""
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    type_map = {".xlsx": SubmissionType.excel, ".xls": SubmissionType.excel,
                ".pdf": SubmissionType.pdf, ".dpr": SubmissionType.dpr}
    submission_type = type_map.get(ext, SubmissionType.excel)

    # Save file
    save_name = f"{uuid.uuid4()}_{filename}"
    save_path = UPLOAD_DIR / save_name
    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    parsed_date: date | None = None
    if submission_date:
        try:
            parsed_date = date.fromisoformat(submission_date)
        except ValueError:
            pass

    submission = FieldSubmission(
        project_id=project_id,
        submitted_by=current_user.id,
        submission_type=submission_type,
        file_path=str(save_path),
        discipline=discipline,
        submission_date=parsed_date or date.today(),
        processing_status=ProcessingStatus.pending,
    )
    db.add(submission)
    await db.flush()
    sub_id = submission.id
    await db.commit()

    try:
        from app.tasks.ingest_tasks import process_file_submission
        process_file_submission.delay(str(sub_id))
    except Exception:
        pass

    await db.refresh(submission)
    return SubmissionResponse.model_validate(submission)


# ---------------------------------------------------------------------------
# POST /api/ingest/voice
# ---------------------------------------------------------------------------

@router.post("/voice", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_voice(
    project_id: uuid.UUID = Form(...),
    discipline: str = Form(None),
    submission_date: str = Form(None),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """Accept audio file, save, and queue for speech-to-text + extraction."""
    filename = audio.filename or "audio.wav"
    save_name = f"{uuid.uuid4()}_{filename}"
    audio_path = UPLOAD_DIR / save_name
    async with aiofiles.open(audio_path, "wb") as f:
        content = await audio.read()
        await f.write(content)

    parsed_date: date | None = None
    if submission_date:
        try:
            parsed_date = date.fromisoformat(submission_date)
        except ValueError:
            pass

    submission = FieldSubmission(
        project_id=project_id,
        submitted_by=current_user.id,
        submission_type=SubmissionType.voice,
        audio_path=str(audio_path),
        discipline=discipline,
        submission_date=parsed_date or date.today(),
        processing_status=ProcessingStatus.pending,
    )
    db.add(submission)
    await db.flush()
    sub_id = submission.id
    await db.commit()

    try:
        from app.tasks.ingest_tasks import process_text_submission
        process_text_submission.delay(str(sub_id))
    except Exception:
        pass

    await db.refresh(submission)
    return SubmissionResponse.model_validate(submission)


# ---------------------------------------------------------------------------
# GET /api/ingest/submissions/{id}
# ---------------------------------------------------------------------------

@router.get("/submissions/{submission_id}", response_model=SubmissionStatus)
async def get_submission_status(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionStatus:
    """Return submission processing status with extracted events and matches."""
    result = await db.execute(
        select(FieldSubmission)
        .where(FieldSubmission.id == submission_id)
        .options(
            selectinload(FieldSubmission.extracted_events).selectinload(
                ExtractedEvent.matches
            )
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    events = [ExtractedEventResponse.model_validate(e) for e in submission.extracted_events]
    matches: list[MatchResponse] = []
    for event in submission.extracted_events:
        for m in event.matches:
            matches.append(MatchResponse.model_validate(m))

    return SubmissionStatus(
        id=submission.id,
        processing_status=submission.processing_status.value,
        extracted_events=events,
        matches=matches,
    )


# ---------------------------------------------------------------------------
# GET /api/ingest/submissions  (list)
# ---------------------------------------------------------------------------

@router.get("/submissions", response_model=list[SubmissionResponse])
async def list_submissions(
    project_id: uuid.UUID | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SubmissionResponse]:
    """List recent field submissions, optionally filtered by project."""
    query = select(FieldSubmission).order_by(FieldSubmission.created_at.desc()).limit(limit)
    if project_id:
        query = query.where(FieldSubmission.project_id == project_id)
    result = await db.execute(query)
    return [SubmissionResponse.model_validate(s) for s in result.scalars().all()]
