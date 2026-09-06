"""AI service proxy routes – forecasts, RAG memory queries, anomaly management."""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import AnomalyFlag, AnomalyStatus, PerformanceMetric, Project, User
from app.schemas.schemas import AnomalyResponse, MetricResponse
from app.services.audit_service import log_action

router = APIRouter(prefix="/ai", tags=["ai"])


# ---------------------------------------------------------------------------
# Mock forecast data generator
# ---------------------------------------------------------------------------

def _mock_forecast(project_id: str) -> dict[str, Any]:
    import random
    random.seed(str(project_id))
    spi = round(random.uniform(0.75, 1.10), 4)
    cpi = round(random.uniform(0.80, 1.05), 4)
    return {
        "project_id": project_id,
        "spi": spi,
        "cpi": cpi,
        "delay_risk_score": round(max(0.0, 1.0 - spi), 3),
        "predicted_finish": "2026-03-15",
        "forecast_explanation": (
            "Based on current progress velocity and historical delay patterns for "
            "this discipline and season, a moderate delay is forecasted. "
            "Key risk: monsoon-season material delivery delays."
        ),
        "recommendations": [
            "Accelerate welding crew deployment for section C-D",
            "Pre-position pipe fittings before monsoon onset",
            "Increase daily reporting frequency to improve data confidence",
        ],
        "source": "mock",
    }


# ---------------------------------------------------------------------------
# GET /api/ai/forecast/{project_id}
# ---------------------------------------------------------------------------

@router.get("/forecast", response_model=dict)
@router.get("/forecast/{project_id}", response_model=dict)
async def get_forecast(
    project_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return AI forecast for the project. Uses mock if MOCK_AI_MODE=True."""
    if not project_id:
        result = await db.execute(select(Project.id).limit(1))
        project_id = result.scalar_one_or_none() or uuid.uuid4()

    if settings.MOCK_AI_MODE:
        return _mock_forecast(str(project_id))

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{settings.AI_SERVICE_URL}/forecast/{project_id}",
                headers={"X-API-Key": settings.GEMINI_API_KEY},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"AI service error: {exc.response.text}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unreachable: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# POST /api/ai/query-memory & /api/ai/memory/query
# ---------------------------------------------------------------------------

@router.post("/query-memory", response_model=dict)
@router.post("/memory/query", response_model=dict)
async def query_memory(
    request: Request,
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Query the institutional memory vector store via RAG."""
    query_text = payload.get("query") or payload.get("question")
    project_id = payload.get("project_id")
    top_k = payload.get("top_k", 5)

    if not query_text:
        raise HTTPException(status_code=400, detail="'query' or 'question' field is required")

    if settings.MOCK_AI_MODE:
        # Return mock RAG results
        return {
            "answer": "In historical Assam pipeline projects, monsoon precipitation caused a 2-3 week average delay on field pipe laying. Recommendation: pre-position critical spools and complete trench backfilling prior to peak rainfall months.",
            "query": query_text,
            "confidence": 0.92,
            "sources": [
                {
                    "id": "src-1",
                    "project_name": "Kaziranga Natural Gas Pipeline (2019)",
                    "activity_name": "Pipe Laying & Trench Excavation",
                    "date": "2019-08-14",
                    "excerpt": "Monsoon flooding caused trench bank collapse at chainage 12+300. Pre-positioning pumps and sandbags mitigated further erosion.",
                    "relevance": 0.94,
                },
                {
                    "id": "src-2",
                    "project_name": "Duliajan Compressor Station (2022)",
                    "activity_name": "Welding Suction Manifold",
                    "date": "2022-07-22",
                    "excerpt": "Field weld productivity dropped 35% during rain spells due to mandatory NDT preheat delays. Shelter tents improved daily weld completion.",
                    "relevance": 0.88,
                }
            ],
            "results": [
                {
                    "score": 0.92,
                    "text": "In KPE-2019, monsoon delays caused 3-week slippage on pipe laying. Mitigation: pre-position materials by April.",
                    "source": "institutional_memory",
                    "project_code": "KPE-2019",
                    "discipline": "piping",
                }
            ],
            "source": "mock",
        }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/query-memory",
                json={"question": query_text, "project_id": project_id, "top_k": top_k},
                headers={"X-API-Key": settings.GEMINI_API_KEY},
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service unreachable: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# GET /api/ai/anomalies
# ---------------------------------------------------------------------------

@router.get("/anomalies", response_model=list[AnomalyResponse])
@router.get("/anomalies/{project_id}", response_model=list[AnomalyResponse])
async def get_anomalies(
    project_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnomalyResponse]:
    """Return all anomaly flags for a project."""
    stmt = select(AnomalyFlag).order_by(AnomalyFlag.created_at.desc())
    if project_id:
        stmt = stmt.where(AnomalyFlag.project_id == project_id)
    result = await db.execute(stmt)
    anomalies = result.scalars().all()
    return [AnomalyResponse.model_validate(a) for a in anomalies]


# ---------------------------------------------------------------------------
# POST /api/ai/anomalies/{id}/resolve
# ---------------------------------------------------------------------------

@router.post("/anomalies/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(
    request: Request,
    anomaly_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnomalyResponse:
    """Mark an anomaly as resolved."""
    result = await db.execute(
        select(AnomalyFlag).where(AnomalyFlag.id == anomaly_id)
    )
    anomaly = result.scalar_one_or_none()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.status = AnomalyStatus.resolved
    anomaly.resolved_by = current_user.id
    anomaly.resolved_at = datetime.now(timezone.utc)

    await log_action(
        db=db,
        user_id=current_user.id,
        action="resolve_anomaly",
        entity="anomaly_flag",
        entity_id=anomaly.id,
        old_value={"status": "open"},
        new_value={"status": "resolved"},
        ip=request.client.host if request.client else None,
    )
    await db.commit()
    await db.refresh(anomaly)
    return AnomalyResponse.model_validate(anomaly)
