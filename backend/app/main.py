"""NEXUS PM – FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup/shutdown logic using the modern lifespan context manager."""
    # Startup
    await create_tables()
    yield
    # Shutdown (nothing special needed)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "NEXUS PM – AI-powered construction project management backend. "
        "Provides field data ingestion, AI extraction, schedule matching, "
        "analytics, and institutional memory querying."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – open for hackathon
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from app.api.ai import router as ai_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.ingest import router as ingest_router
from app.api.matches import router as matches_router
from app.api.projects import router as projects_router

app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(matches_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(ai_router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Returns application health status."""
    return {
        "status": "ok",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
    }


@app.get("/", tags=["system"], include_in_schema=False)
async def root() -> dict:
    return {"message": f"Welcome to {settings.PROJECT_NAME} API", "docs": "/docs"}
