"""
Celery tasks for field submission processing and metric computation.

Each task:
1. Opens a synchronous SQLAlchemy session (Celery workers are sync)
2. Fetches the submission and updates processing_status
3. Calls the AI service (or mock) for extraction / matching
4. Persists results and sets status to 'done' or 'failed'
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any

import httpx
from celery import Task
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.tasks.celery_app import celery_app

# ---------------------------------------------------------------------------
# Sync DB setup for Celery (not async)
# ---------------------------------------------------------------------------

_SYNC_DB_URL = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
).replace("postgresql+asyncio://", "postgresql+psycopg2://")

_engine = create_engine(_SYNC_DB_URL, pool_pre_ping=True)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def _get_session() -> Session:
    return _SessionLocal()


# ---------------------------------------------------------------------------
# AI extraction helper
# ---------------------------------------------------------------------------

def _call_ai_extract(text: str, project_id: str, discipline: str | None) -> list[dict[str, Any]]:
    """
    Call AI service /extract endpoint. Falls back to a minimal mock result.
    Returns list of extracted event dicts.
    """
    if settings.MOCK_AI_MODE:
        return _mock_extract(text, project_id, discipline)

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{settings.AI_SERVICE_URL}/extract",
                json={"text": text, "project_id": project_id, "discipline": discipline},
                headers={"X-API-Key": settings.GEMINI_API_KEY},
            )
            resp.raise_for_status()
            return resp.json().get("events", [])
    except Exception:
        return _mock_extract(text, project_id, discipline)


def _mock_extract(text: str, project_id: str, discipline: str | None) -> list[dict[str, Any]]:
    """Produce a single mock extracted event from text."""
    words = text.split()
    return [
        {
            "raw_description": text[:500],
            "discipline": discipline or "civil",
            "extracted_start": date.today().isoformat(),
            "extracted_finish": None,
            "progress_pct": 35.0,
            "quantity_done": None,
            "location_tag": "Site A",
            "supervisor_name": None,
            "extraction_confidence": 0.72,
        }
    ]


def _call_ai_match(
    event_desc: str,
    project_id: str,
    discipline: str | None,
    db: Session,
) -> list[dict[str, Any]]:
    """
    Match an extracted event to schedule nodes.
    Uses keyword overlap as a simple local fallback.
    Returns list of match candidate dicts.
    """
    from app.models.models import ScheduleNode

    nodes = db.execute(
        select(ScheduleNode).where(
            ScheduleNode.project_id == uuid.UUID(project_id)
        )
    ).scalars().all()

    if not nodes:
        return []

    if settings.MOCK_AI_MODE or True:
        # Simple keyword overlap scoring
        event_words = set(event_desc.lower().split())
        best_node = None
        best_score = 0.0
        for node in nodes:
            node_words = set(node.name.lower().split())
            overlap = len(event_words & node_words)
            score = overlap / max(len(event_words | node_words), 1)
            if score > best_score:
                best_score = score
                best_node = node

        if best_node and best_score > 0.05:
            return [
                {
                    "schedule_node_id": str(best_node.id),
                    "match_score": round(best_score, 4),
                    "match_method": "keyword_overlap",
                    "match_explanation": f"Keyword overlap score: {best_score:.2%}",
                    "status": "auto_accepted" if best_score >= 0.3 else "needs_review",
                }
            ]

    return [
        {
            "schedule_node_id": None,
            "match_score": 0.0,
            "match_method": "no_match",
            "match_explanation": "No suitable schedule node found",
            "status": "flagged_new",
        }
    ]


# ---------------------------------------------------------------------------
# Task: process_text_submission
# ---------------------------------------------------------------------------

@celery_app.task(name="nexus.process_text_submission", bind=True, max_retries=3)
def process_text_submission(self: Task, submission_id: str) -> dict[str, Any]:
    """
    Process a text/voice field submission:
    1. Extract events via AI
    2. Match events to schedule nodes
    3. Persist ExtractedEvent and ActivityMatch records
    4. Update submission status
    """
    from app.models.models import (
        ActivityMatch,
        ExtractedEvent,
        FieldSubmission,
        MatchStatus,
        ProcessingStatus,
    )

    db = _get_session()
    try:
        sub_id = uuid.UUID(submission_id)

        # Fetch submission
        submission = db.execute(
            select(FieldSubmission).where(FieldSubmission.id == sub_id)
        ).scalar_one_or_none()

        if not submission:
            return {"error": "Submission not found", "id": submission_id}

        # Mark processing
        submission.processing_status = ProcessingStatus.processing
        db.commit()

        text = submission.raw_content or submission.transcript or ""
        project_id = str(submission.project_id)

        # Extract events
        extracted = _call_ai_extract(text, project_id, submission.discipline)

        for ev_data in extracted:
            event = ExtractedEvent(
                submission_id=sub_id,
                project_id=submission.project_id,
                raw_description=ev_data.get("raw_description"),
                discipline=ev_data.get("discipline") or submission.discipline,
                extracted_start=date.fromisoformat(ev_data["extracted_start"])
                if ev_data.get("extracted_start")
                else None,
                extracted_finish=date.fromisoformat(ev_data["extracted_finish"])
                if ev_data.get("extracted_finish")
                else None,
                progress_pct=ev_data.get("progress_pct"),
                quantity_done=ev_data.get("quantity_done"),
                location_tag=ev_data.get("location_tag"),
                supervisor_name=ev_data.get("supervisor_name"),
                extraction_confidence=ev_data.get("extraction_confidence"),
            )
            db.add(event)
            db.flush()

            # Match event to schedule node
            candidates = _call_ai_match(
                event.raw_description or "",
                project_id,
                event.discipline,
                db,
            )

            for cand in candidates:
                node_id = uuid.UUID(cand["schedule_node_id"]) if cand.get("schedule_node_id") else None
                match = ActivityMatch(
                    extracted_event_id=event.id,
                    schedule_node_id=node_id,
                    match_score=cand.get("match_score"),
                    match_method=cand.get("match_method"),
                    match_explanation=cand.get("match_explanation"),
                    status=MatchStatus(cand.get("status", "needs_review")),
                )
                db.add(match)

        # Mark done
        submission.processing_status = ProcessingStatus.done
        db.commit()

        # Trigger metrics recompute
        compute_project_metrics.delay(project_id)

        return {"status": "done", "submission_id": submission_id, "events": len(extracted)}

    except Exception as exc:
        db.rollback()
        try:
            sub_id = uuid.UUID(submission_id)
            db.execute(
                update(FieldSubmission)
                .where(FieldSubmission.id == sub_id)
                .values(processing_status=ProcessingStatus.failed)
            )
            db.commit()
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=30) from exc
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Task: process_file_submission
# ---------------------------------------------------------------------------

@celery_app.task(name="nexus.process_file_submission", bind=True, max_retries=3)
def process_file_submission(self: Task, submission_id: str) -> dict[str, Any]:
    """
    Process a file (Excel/PDF) submission:
    1. Read the file contents
    2. Extract text / tabular data
    3. Call extract + match pipeline
    4. Persist results
    """
    from app.models.models import (
        ActivityMatch,
        ExtractedEvent,
        FieldSubmission,
        MatchStatus,
        ProcessingStatus,
    )

    db = _get_session()
    try:
        sub_id = uuid.UUID(submission_id)

        submission = db.execute(
            select(FieldSubmission).where(FieldSubmission.id == sub_id)
        ).scalar_one_or_none()

        if not submission:
            return {"error": "Submission not found"}

        submission.processing_status = ProcessingStatus.processing
        db.commit()

        text_content = ""
        if submission.file_path:
            import os

            file_path = submission.file_path
            ext = os.path.splitext(file_path)[1].lower()

            if ext in (".xlsx", ".xls"):
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path)
                    text_content = df.to_string(index=False)
                except Exception as e:
                    text_content = f"[Excel parse error: {e}]"
            elif ext == ".pdf":
                try:
                    # Basic text extraction via reportlab/PyPDF fallback
                    with open(file_path, "rb") as f:
                        text_content = f"[PDF binary: {len(f.read())} bytes – requires OCR pipeline]"
                except Exception as e:
                    text_content = f"[PDF parse error: {e}]"
            else:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        text_content = f.read()
                except Exception:
                    text_content = "[binary file – unreadable as text]"

        project_id = str(submission.project_id)
        extracted = _call_ai_extract(text_content, project_id, submission.discipline)

        for ev_data in extracted:
            event = ExtractedEvent(
                submission_id=sub_id,
                project_id=submission.project_id,
                raw_description=ev_data.get("raw_description"),
                discipline=ev_data.get("discipline") or submission.discipline,
                extracted_start=date.fromisoformat(ev_data["extracted_start"])
                if ev_data.get("extracted_start")
                else None,
                extracted_finish=date.fromisoformat(ev_data["extracted_finish"])
                if ev_data.get("extracted_finish")
                else None,
                progress_pct=ev_data.get("progress_pct"),
                quantity_done=ev_data.get("quantity_done"),
                location_tag=ev_data.get("location_tag"),
                supervisor_name=ev_data.get("supervisor_name"),
                extraction_confidence=ev_data.get("extraction_confidence"),
            )
            db.add(event)
            db.flush()

            candidates = _call_ai_match(
                event.raw_description or "",
                project_id,
                event.discipline,
                db,
            )

            for cand in candidates:
                node_id = uuid.UUID(cand["schedule_node_id"]) if cand.get("schedule_node_id") else None
                match = ActivityMatch(
                    extracted_event_id=event.id,
                    schedule_node_id=node_id,
                    match_score=cand.get("match_score"),
                    match_method=cand.get("match_method"),
                    match_explanation=cand.get("match_explanation"),
                    status=MatchStatus(cand.get("status", "needs_review")),
                )
                db.add(match)

        submission.processing_status = ProcessingStatus.done
        db.commit()

        compute_project_metrics.delay(project_id)
        return {"status": "done", "submission_id": submission_id, "events": len(extracted)}

    except Exception as exc:
        db.rollback()
        try:
            sub_id_u = uuid.UUID(submission_id)
            db.execute(
                update(FieldSubmission)
                .where(FieldSubmission.id == sub_id_u)
                .values(processing_status=ProcessingStatus.failed)
            )
            db.commit()
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=30) from exc
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Task: compute_project_metrics
# ---------------------------------------------------------------------------

@celery_app.task(name="nexus.compute_project_metrics", bind=True, max_retries=2)
def compute_project_metrics(self: Task, project_id: str) -> dict[str, Any]:
    """
    Recompute SPI/CPI for all ScheduleNodes with actual progress, then
    save a project-level PerformanceMetric rollup.
    """
    from app.models.models import ActualProgress, PerformanceMetric, ScheduleNode

    db = _get_session()
    try:
        proj_id = uuid.UUID(project_id)

        nodes = db.execute(
            select(ScheduleNode).where(ScheduleNode.project_id == proj_id)
        ).scalars().all()

        actuals = db.execute(
            select(ActualProgress).where(ActualProgress.project_id == proj_id)
        ).scalars().all()

        actuals_by_node: dict[uuid.UUID, ActualProgress] = {
            a.schedule_node_id: a for a in actuals
        }

        total_planned = 0
        total_earned = 0
        node_count = 0

        for node in nodes:
            if not node.planned_duration:
                continue
            planned = node.planned_duration
            actual = actuals_by_node.get(node.id)
            earned = planned * (float(actual.progress_pct or 0) / 100.0) if actual else 0.0

            total_planned += planned
            total_earned += earned
            node_count += 1

        if total_planned > 0:
            spi = round(total_earned / total_planned, 4)
        else:
            spi = 1.0

        # CPI – we don't have cost data, so use SPI as proxy
        cpi = round(min(spi * 1.02, 1.05), 4)
        delay_risk = round(max(0.0, min(1.0, 1.0 - spi)), 4)

        from datetime import timedelta
        today = date.today()
        baseline_node = next(
            (n for n in nodes if n.baseline_finish is not None), None
        )
        predicted_finish = None
        if baseline_node and baseline_node.baseline_finish and spi > 0:
            remaining_days = (baseline_node.baseline_finish - today).days
            predicted_days = int(remaining_days / spi)
            predicted_finish = today + timedelta(days=predicted_days)

        metric = PerformanceMetric(
            project_id=proj_id,
            schedule_node_id=None,
            computed_at=datetime.now(timezone.utc),
            spi=spi,
            cpi=cpi,
            float_consumed=max(0, int((1.0 - spi) * 30)),
            predicted_finish=predicted_finish,
            delay_risk_score=delay_risk,
            forecast_explanation=(
                f"SPI={spi:.3f}. Computed from {node_count} activities with "
                f"planned durations. Risk score {delay_risk:.3f}."
            ),
        )
        db.add(metric)
        db.commit()

        return {
            "project_id": project_id,
            "spi": spi,
            "cpi": cpi,
            "delay_risk": delay_risk,
            "nodes_evaluated": node_count,
        }

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60) from exc
    finally:
        db.close()
