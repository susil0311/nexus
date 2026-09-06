"""
NEXUS PM AI Service – FastAPI Main Application
Port: 8001
"""
from __future__ import annotations

import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("nexus.ai-service")

# ── Global component instances ────────────────────────────────────────────────
_extractor = None
_matcher = None
_forecaster = None
_sentinel = None
_rag_engine = None


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all AI components on startup."""
    global _extractor, _matcher, _forecaster, _sentinel, _rag_engine
    logger.info("=" * 60)
    logger.info("NEXUS PM AI Service starting up …")
    logger.info("MOCK_MODE = %s", settings.MOCK_MODE)
    logger.info("=" * 60)

    # 1. NLP Extractor
    try:
        from extractor.nlp_extractor import NLPExtractor
        _extractor = NLPExtractor()
        logger.info("[OK] NLPExtractor initialized")
    except Exception as exc:
        logger.error("[FAIL] NLPExtractor: %s", exc)

    # 2. Fuzzy Matcher
    try:
        from matcher.fuzzy_matcher import FuzzyMatcher
        _matcher = FuzzyMatcher()
        logger.info("[OK] FuzzyMatcher initialized")
    except Exception as exc:
        logger.error("[FAIL] FuzzyMatcher: %s", exc)

    # 3. Delay Forecaster – train on synthetic data
    try:
        from forecaster.delay_forecaster import DelayForecaster
        _forecaster = DelayForecaster()
        _forecaster.train_on_synthetic()
        logger.info("[OK] DelayForecaster trained")
    except Exception as exc:
        logger.error("[FAIL] DelayForecaster: %s", exc)

    # 4. Anomaly Sentinel
    try:
        from anomaly.sentinel import AnomalySentinel
        _sentinel = AnomalySentinel()
        logger.info("[OK] AnomalySentinel initialized")
    except Exception as exc:
        logger.error("[FAIL] AnomalySentinel: %s", exc)

    # 5. RAG Engine – seed institutional memory
    try:
        from memory.rag_engine import RAGEngine
        _rag_engine = RAGEngine()
        _rag_engine.seed_memory()
        logger.info("[OK] RAGEngine initialized and seeded")
    except Exception as exc:
        logger.error("[FAIL] RAGEngine: %s", exc)

    logger.info("NEXUS PM AI Service ready on port %d", settings.AI_SERVICE_PORT)
    yield

    logger.info("NEXUS PM AI Service shutting down")


# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="NEXUS PM AI Service",
    description=(
        "AI backend for NEXUS Project Management platform. "
        "Provides NLP extraction, semantic matching, delay forecasting, "
        "anomaly detection, and institutional memory RAG."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _require(component, name: str):
    if component is None:
        raise HTTPException(status_code=503, detail=f"{name} is not initialized")
    return component


# ══════════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class ExtractTextRequest(BaseModel):
    text: str = Field(..., description="Raw DPR or field report text")
    discipline: str = Field("General", description="Discipline hint (e.g. Piping, Civil)")
    project_context: dict[str, Any] = Field(default_factory=dict)


class ExtractTextResponse(BaseModel):
    events: list[dict[str, Any]]
    count: int
    source: str = "text"


class MatchRequest(BaseModel):
    events: list[dict[str, Any]] = Field(..., description="Extracted events from NLP extractor")
    project_id: str = Field(..., description="Project identifier for ChromaDB lookup")
    schedule_nodes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Optional: schedule nodes to index before matching",
    )


class MatchResponse(BaseModel):
    matches: list[dict[str, Any]]
    count: int
    auto_accepted: int
    needs_review: int
    new_activities: int


class IndexNodesRequest(BaseModel):
    project_id: str
    nodes: list[dict[str, Any]] = Field(..., description="WBS / schedule nodes to index")


class IndexNodesResponse(BaseModel):
    project_id: str
    indexed: int


class ForecastRequest(BaseModel):
    spi: float = Field(1.0, description="Schedule Performance Index")
    planned_duration_days: int = Field(180)
    elapsed_pct: float = Field(50.0, description="Percentage of planned duration elapsed")
    discipline: str = Field("General")
    float_days: float = Field(0.0, description="Total float on critical path")
    num_resources: int = Field(30)
    planned_finish_date: str = Field("", description="Planned finish date YYYY-MM-DD")
    productivity_notes: str = Field("", description="Freeform productivity context for narrative")


class QueryMemoryRequest(BaseModel):
    question: str = Field(..., description="Natural language question for institutional memory")
    context: dict[str, Any] = Field(default_factory=dict, description="Current project context")


class AnomalyCheckRequest(BaseModel):
    events: list[dict[str, Any]] = Field(..., description="Events to check for anomalies")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """Service health check."""
    return {
        "status": "ok",
        "service": "nexus-pm-ai-service",
        "version": "1.0.0",
        "mock_mode": settings.MOCK_MODE,
        "components": {
            "extractor": _extractor is not None,
            "matcher": _matcher is not None,
            "forecaster": _forecaster is not None,
            "sentinel": _sentinel is not None,
            "rag_engine": _rag_engine is not None,
        },
    }


# ── Extraction ──────────────────────────────────────────────────────────────────

@app.post("/extract/text", response_model=ExtractTextResponse, tags=["Extraction"])
async def extract_from_text(request: ExtractTextRequest):
    """
    Extract structured activity events from DPR / field report text using Gemini.
    Returns a list of activity event dicts.
    """
    extractor = _require(_extractor, "NLPExtractor")
    events = extractor.extract_from_text(
        text=request.text,
        discipline=request.discipline,
        project_context=request.project_context,
    )
    return ExtractTextResponse(events=events, count=len(events), source="text")


@app.post("/extract/file", tags=["Extraction"])
async def extract_from_file(
    file: UploadFile = File(...),
    discipline: str = Form("General"),
):
    """
    Upload an Excel (.xlsx) file and extract activity events using Gemini.
    """
    extractor = _require(_extractor, "NLPExtractor")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".xlsx", ".xls", ".csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: .xlsx, .xls, .csv",
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        events = extractor.extract_from_excel(file_path=tmp_path, discipline=discipline)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return {
        "events": events,
        "count": len(events),
        "source": "file",
        "filename": file.filename,
    }


# ── Matching ──────────────────────────────────────────────────────────────────

@app.post("/index-nodes", response_model=IndexNodesResponse, tags=["Matching"])
async def index_nodes(request: IndexNodesRequest):
    """
    Index WBS / schedule nodes for a project into ChromaDB for semantic matching.
    """
    matcher = _require(_matcher, "FuzzyMatcher")
    indexed = matcher._embedder.index_schedule_nodes(
        nodes=request.nodes, project_id=request.project_id
    )
    return IndexNodesResponse(project_id=request.project_id, indexed=indexed)


@app.post("/match", response_model=MatchResponse, tags=["Matching"])
async def match_events(request: MatchRequest):
    """
    Match extracted field events to baseline schedule nodes using semantic search.
    Optionally indexes provided schedule_nodes before matching.
    """
    matcher = _require(_matcher, "FuzzyMatcher")

    # Auto-index nodes if provided
    if request.schedule_nodes:
        matcher._embedder.index_schedule_nodes(
            nodes=request.schedule_nodes, project_id=request.project_id
        )

    matches = matcher.match_batch(events=request.events, project_id=request.project_id)

    auto_accepted = sum(
        1 for m in matches
        if m.get("top_match", {}).get("match_status") == "auto_accepted"
    )
    needs_review = sum(
        1 for m in matches
        if m.get("needs_review", False) and not m.get("is_new_activity", False)
    )
    new_activities = sum(1 for m in matches if m.get("is_new_activity", False))

    return MatchResponse(
        matches=matches,
        count=len(matches),
        auto_accepted=auto_accepted,
        needs_review=needs_review,
        new_activities=new_activities,
    )


# ── Forecasting ───────────────────────────────────────────────────────────────

@app.post("/forecast/{project_id}", tags=["Forecasting"])
async def forecast_project(project_id: str, request: ForecastRequest):
    """
    Predict project delay and generate a narrative using XGBoost + Gemini.
    """
    forecaster = _require(_forecaster, "DelayForecaster")

    metrics = request.model_dump()
    metrics["project_id"] = project_id

    forecast = forecaster.predict(project_metrics=metrics)
    forecast["project_id"] = project_id
    return forecast


@app.get("/forecast/{project_id}", tags=["Forecasting"])
async def forecast_project_get(
    project_id: str,
    spi: float = Query(1.0),
    planned_duration_days: int = Query(180),
    elapsed_pct: float = Query(50.0),
    discipline: str = Query("General"),
    float_days: float = Query(0.0),
    num_resources: int = Query(30),
    planned_finish_date: str = Query(""),
):
    """
    GET version of forecast endpoint with query parameters (for quick testing).
    """
    forecaster = _require(_forecaster, "DelayForecaster")
    metrics = {
        "spi": spi,
        "planned_duration_days": planned_duration_days,
        "elapsed_pct": elapsed_pct,
        "discipline": discipline,
        "float_days": float_days,
        "num_resources": num_resources,
        "planned_finish_date": planned_finish_date,
        "project_id": project_id,
    }
    forecast = forecaster.predict(project_metrics=metrics)
    forecast["project_id"] = project_id
    return forecast


# ── Institutional Memory / RAG ────────────────────────────────────────────────

@app.post("/query-memory", tags=["Memory"])
async def query_memory(request: QueryMemoryRequest):
    """
    Query institutional memory using RAG: retrieve past project records,
    synthesize an answer with Gemini.
    """
    rag = _require(_rag_engine, "RAGEngine")
    result = rag.query(question=request.question, context=request.context)
    return result


@app.post("/index-memory", tags=["Memory"])
async def index_memory(records: list[dict[str, Any]]):
    """
    Add new records to the institutional memory database.
    """
    rag = _require(_rag_engine, "RAGEngine")
    count = rag.index_memory(records=records)
    return {"indexed": count, "total": _rag_engine._collection.count()}


# ── Anomaly Detection ─────────────────────────────────────────────────────────

@app.post("/check-anomalies", tags=["Anomaly Detection"])
async def check_anomalies(request: AnomalyCheckRequest):
    """
    Run anomaly detection on extracted events.
    Returns events with flagged anomalies (progress overclaim, timeline reversal, etc.)
    """
    sentinel = _require(_sentinel, "AnomalySentinel")
    results = sentinel.check_batch(events=request.events)
    flagged = [r for r in results if r.get("has_anomalies", False)]
    return {
        "total_events": len(request.events),
        "flagged_events": len(flagged),
        "results": results,
    }


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.AI_SERVICE_PORT,
        reload=True,
        log_level="info",
    )
