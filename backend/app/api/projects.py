"""Projects API routes."""
import io
import uuid
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Project, ScheduleNode, User
from app.schemas.schemas import (
    ProjectCreate,
    ProjectListItem,
    ProjectResponse,
    ScheduleNodeCreate,
    ScheduleNodeResponse,
)
from app.services.audit_service import log_action

router = APIRouter(prefix="/projects", tags=["projects"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_tree(
    nodes: list[ScheduleNode],
    parent_id: Optional[uuid.UUID] = None,
) -> list[ScheduleNodeResponse]:
    """Recursively build a tree of ScheduleNodeResponse objects."""
    result = []
    for node in nodes:
        if node.parent_id == parent_id:
            schema = ScheduleNodeResponse.model_validate(node)
            schema.children = _build_tree(nodes, node.id)
            result.append(schema)
    return result


# ---------------------------------------------------------------------------
# GET /api/projects
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ProjectListItem])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectListItem]:
    """Return all projects visible to the current user."""
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    return [ProjectListItem.model_validate(p) for p in projects]


# ---------------------------------------------------------------------------
# POST /api/projects
# ---------------------------------------------------------------------------

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request,
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    """Create a new project."""
    # Check code uniqueness
    existing = await db.execute(select(Project).where(Project.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project code '{payload.code}' already exists",
        )

    project = Project(
        name=payload.name,
        code=payload.code,
        client=payload.client,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        baseline_start=payload.baseline_start,
        baseline_end=payload.baseline_end,
        status=payload.status,  # type: ignore[arg-type]
        metadata_=payload.metadata,
    )
    db.add(project)
    await db.flush()

    await log_action(
        db=db,
        user_id=current_user.id,
        action="create",
        entity="project",
        entity_id=project.id,
        old_value=None,
        new_value={"name": project.name, "code": project.code},
        ip=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


# ---------------------------------------------------------------------------
# GET /api/projects/{id}
# ---------------------------------------------------------------------------

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


# ---------------------------------------------------------------------------
# GET /api/projects/{id}/schedule  (tree)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/schedule", response_model=list[ScheduleNodeResponse])
async def get_schedule_tree(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScheduleNodeResponse]:
    """Return the WBS schedule as a nested tree."""
    result = await db.execute(
        select(ScheduleNode)
        .where(ScheduleNode.project_id == project_id)
        .order_by(ScheduleNode.level, ScheduleNode.activity_id)
    )
    nodes = list(result.scalars().all())
    return _build_tree(nodes, parent_id=None)


# ---------------------------------------------------------------------------
# POST /api/projects/{id}/schedule/import
# ---------------------------------------------------------------------------

@router.post("/{project_id}/schedule/import", response_model=dict)
async def import_schedule(
    request: Request,
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Import schedule nodes from a CSV or JSON file.

    Expected CSV columns:
        activity_id, parent_id (optional), level, discipline, name,
        baseline_start (YYYY-MM-DD), baseline_finish (YYYY-MM-DD),
        planned_duration, planned_quantity, unit, is_milestone, float_days
    """
    # Ensure project exists
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.endswith(".json"):
            import json
            rows: list[dict[str, Any]] = json.loads(content)
        elif filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
            rows = df.where(pd.notnull(df), None).to_dict(orient="records")
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only .csv and .json files are supported",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc

    # Map activity_id -> db UUID for parent resolution
    id_map: dict[str, uuid.UUID] = {}
    created = 0

    for row in rows:
        node = ScheduleNode(
            project_id=project_id,
            activity_id=str(row.get("activity_id", "")),
            level=int(row.get("level", 1)),
            discipline=row.get("discipline"),
            name=str(row.get("name", "")),
            baseline_start=row.get("baseline_start") or None,
            baseline_finish=row.get("baseline_finish") or None,
            planned_duration=int(row["planned_duration"]) if row.get("planned_duration") else None,
            planned_quantity=float(row["planned_quantity"]) if row.get("planned_quantity") else None,
            unit=row.get("unit"),
            is_milestone=bool(row.get("is_milestone", False)),
            float_days=int(row["float_days"]) if row.get("float_days") else None,
        )
        # Resolve parent
        parent_aid = str(row.get("parent_id", "")) if row.get("parent_id") else None
        if parent_aid and parent_aid in id_map:
            node.parent_id = id_map[parent_aid]

        db.add(node)
        await db.flush()
        id_map[node.activity_id] = node.id
        created += 1

    await db.commit()
    await log_action(
        db=db,
        user_id=current_user.id,
        action="import_schedule",
        entity="project",
        entity_id=project_id,
        old_value=None,
        new_value={"rows_imported": created},
        ip=request.client.host if request.client else None,
    )
    return {"imported": created, "project_id": str(project_id)}
