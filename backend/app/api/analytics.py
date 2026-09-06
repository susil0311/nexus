"""Analytics API routes – dashboard, SPI trend, discipline breakdown, portfolio."""
import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    ActualProgress,
    AnomalyFlag,
    AnomalyStatus,
    FieldSubmission,
    PerformanceMetric,
    Project,
    ScheduleNode,
    User,
)
from app.schemas.schemas import MetricResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------------------------------------------------------------------------
# GET /api/analytics/{project_id}/dashboard
# ---------------------------------------------------------------------------

@router.get("/{project_id}/dashboard", response_model=dict)
async def project_dashboard(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Return high-level KPIs for the project dashboard."""

    # Total activities
    total_result = await db.execute(
        select(func.count(ScheduleNode.id)).where(ScheduleNode.project_id == project_id)
    )
    total_activities: int = total_result.scalar() or 0

    # Completed activities (progress_pct == 100)
    completed_result = await db.execute(
        select(func.count(ActualProgress.id)).where(
            ActualProgress.project_id == project_id,
            ActualProgress.is_complete == True,  # noqa: E712
        )
    )
    completed: int = completed_result.scalar() or 0

    # At-risk: activities with delay_risk_score > 0.6
    at_risk_result = await db.execute(
        select(func.count(PerformanceMetric.id)).where(
            PerformanceMetric.project_id == project_id,
            PerformanceMetric.delay_risk_score > 0.6,
        )
    )
    at_risk: int = at_risk_result.scalar() or 0

    # Latest SPI / CPI
    metric_result = await db.execute(
        select(PerformanceMetric)
        .where(
            PerformanceMetric.project_id == project_id,
            PerformanceMetric.schedule_node_id == None,  # noqa: E711  (project-level)
        )
        .order_by(PerformanceMetric.computed_at.desc())
        .limit(1)
    )
    latest_metric = metric_result.scalar_one_or_none()

    # Recent submissions (last 5)
    subs_result = await db.execute(
        select(FieldSubmission)
        .where(FieldSubmission.project_id == project_id)
        .order_by(FieldSubmission.created_at.desc())
        .limit(5)
    )
    recent_submissions = [
        {
            "id": str(s.id),
            "type": s.submission_type.value,
            "status": s.processing_status.value,
            "created_at": s.created_at.isoformat(),
        }
        for s in subs_result.scalars().all()
    ]

    # Open anomalies count
    anomaly_result = await db.execute(
        select(func.count(AnomalyFlag.id)).where(
            AnomalyFlag.project_id == project_id,
            AnomalyFlag.status == AnomalyStatus.open,
        )
    )
    open_anomalies: int = anomaly_result.scalar() or 0

    return {
        "project_id": str(project_id),
        "total_activities": total_activities,
        "completed": completed,
        "in_progress": total_activities - completed,
        "at_risk": at_risk,
        "open_anomalies": open_anomalies,
        "spi": float(latest_metric.spi) if latest_metric and latest_metric.spi else None,
        "cpi": float(latest_metric.cpi) if latest_metric and latest_metric.cpi else None,
        "predicted_finish": latest_metric.predicted_finish.isoformat() if latest_metric and latest_metric.predicted_finish else None,
        "delay_risk_score": float(latest_metric.delay_risk_score) if latest_metric and latest_metric.delay_risk_score else None,
        "recent_submissions": recent_submissions,
        "as_of": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# GET /api/analytics/{project_id}/spi-trend
# ---------------------------------------------------------------------------

@router.get("/{project_id}/spi-trend", response_model=list[dict])
async def spi_trend(
    project_id: uuid.UUID,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Return time-series SPI/CPI data points for a project."""
    query = (
        select(PerformanceMetric)
        .where(
            PerformanceMetric.project_id == project_id,
            PerformanceMetric.schedule_node_id == None,  # noqa: E711
        )
        .order_by(PerformanceMetric.computed_at.asc())
    )
    if from_date:
        query = query.where(PerformanceMetric.computed_at >= datetime(from_date.year, from_date.month, from_date.day))
    if to_date:
        query = query.where(PerformanceMetric.computed_at <= datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59))

    result = await db.execute(query)
    metrics = result.scalars().all()

    return [
        {
            "timestamp": m.computed_at.isoformat(),
            "spi": float(m.spi) if m.spi else None,
            "cpi": float(m.cpi) if m.cpi else None,
            "delay_risk_score": float(m.delay_risk_score) if m.delay_risk_score else None,
            "predicted_finish": m.predicted_finish.isoformat() if m.predicted_finish else None,
        }
        for m in metrics
    ]


# ---------------------------------------------------------------------------
# GET /api/analytics/{project_id}/discipline-breakdown
# ---------------------------------------------------------------------------

@router.get("/{project_id}/discipline-breakdown", response_model=list[dict])
async def discipline_breakdown(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Return per-discipline activity counts and average progress."""
    # Fetch all nodes with discipline
    nodes_result = await db.execute(
        select(ScheduleNode).where(ScheduleNode.project_id == project_id)
    )
    nodes = nodes_result.scalars().all()

    # Fetch all actuals for this project
    actuals_result = await db.execute(
        select(ActualProgress).where(ActualProgress.project_id == project_id)
    )
    actuals = actuals_result.scalars().all()

    actuals_map: dict[uuid.UUID, float] = {
        a.schedule_node_id: float(a.progress_pct or 0) for a in actuals
    }

    disciplines: dict[str, dict[str, Any]] = {}
    for node in nodes:
        disc = node.discipline or "unspecified"
        if disc not in disciplines:
            disciplines[disc] = {"discipline": disc, "total": 0, "completed": 0, "progress_sum": 0.0}
        disciplines[disc]["total"] += 1
        pct = actuals_map.get(node.id, 0.0)
        disciplines[disc]["progress_sum"] += pct
        if pct >= 100.0:
            disciplines[disc]["completed"] += 1

    breakdown = []
    for disc, data in disciplines.items():
        total = data["total"]
        breakdown.append({
            "discipline": disc,
            "total_activities": total,
            "completed": data["completed"],
            "avg_progress_pct": round(data["progress_sum"] / total, 2) if total else 0.0,
        })
    return breakdown


# ---------------------------------------------------------------------------
# GET /api/analytics/portfolio
# ---------------------------------------------------------------------------

@router.get("/portfolio", response_model=list[dict])
async def portfolio_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Return all projects with latest SPI, risk score, and status."""
    proj_result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = proj_result.scalars().all()

    output = []
    for proj in projects:
        metric_result = await db.execute(
            select(PerformanceMetric)
            .where(
                PerformanceMetric.project_id == proj.id,
                PerformanceMetric.schedule_node_id == None,  # noqa: E711
            )
            .order_by(PerformanceMetric.computed_at.desc())
            .limit(1)
        )
        metric = metric_result.scalar_one_or_none()

        # count open anomalies
        anom_result = await db.execute(
            select(func.count(AnomalyFlag.id)).where(
                AnomalyFlag.project_id == proj.id,
                AnomalyFlag.status == AnomalyStatus.open,
            )
        )
        open_anomalies = anom_result.scalar() or 0

        output.append({
            "id": str(proj.id),
            "name": proj.name,
            "code": proj.code,
            "client": proj.client,
            "status": proj.status.value,
            "baseline_start": proj.baseline_start.isoformat() if proj.baseline_start else None,
            "baseline_end": proj.baseline_end.isoformat() if proj.baseline_end else None,
            "spi": float(metric.spi) if metric and metric.spi else None,
            "cpi": float(metric.cpi) if metric and metric.cpi else None,
            "delay_risk_score": float(metric.delay_risk_score) if metric and metric.delay_risk_score else None,
            "predicted_finish": metric.predicted_finish.isoformat() if metric and metric.predicted_finish else None,
            "open_anomalies": open_anomalies,
        })
    return output
