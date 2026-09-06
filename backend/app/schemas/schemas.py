"""Pydantic v2 schemas for NEXUS PM API."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ---------------------------------------------------------------------------
# Generic pagination
# ---------------------------------------------------------------------------
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    role: str
    discipline: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Optional[UserResponse] = None


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    client: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None
    status: str = "active"
    metadata: Optional[dict[str, Any]] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    client: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None
    status: str
    metadata: Optional[dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    client: Optional[str] = None
    location: Optional[str] = None
    status: str
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None


# ---------------------------------------------------------------------------
# Schedule Node
# ---------------------------------------------------------------------------

class ScheduleNodeCreate(BaseModel):
    activity_id: str
    parent_id: Optional[uuid.UUID] = None
    level: int = 1
    discipline: Optional[str] = None
    name: str
    baseline_start: Optional[date] = None
    baseline_finish: Optional[date] = None
    planned_duration: Optional[int] = None
    planned_quantity: Optional[float] = None
    unit: Optional[str] = None
    is_milestone: bool = False
    float_days: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None


class ScheduleNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    project_id: uuid.UUID
    activity_id: str
    parent_id: Optional[uuid.UUID] = None
    level: int
    discipline: Optional[str] = None
    name: str
    baseline_start: Optional[date] = None
    baseline_finish: Optional[date] = None
    planned_duration: Optional[int] = None
    planned_quantity: Optional[float] = None
    unit: Optional[str] = None
    is_milestone: bool
    float_days: Optional[int] = None
    metadata: Optional[dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime
    children: List["ScheduleNodeResponse"] = []


# ---------------------------------------------------------------------------
# Field Submission
# ---------------------------------------------------------------------------

class TextIngestionRequest(BaseModel):
    project_id: uuid.UUID
    content: str = Field(..., min_length=5)
    discipline: Optional[str] = None
    submission_date: Optional[date] = None


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    submission_type: str
    processing_status: str
    discipline: Optional[str] = None
    submission_date: Optional[date] = None
    created_at: datetime


class SubmissionStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processing_status: str
    extracted_events: List["ExtractedEventResponse"] = []
    matches: List["MatchResponse"] = []


# ---------------------------------------------------------------------------
# Extracted Event
# ---------------------------------------------------------------------------

class ExtractedEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    submission_id: uuid.UUID
    project_id: uuid.UUID
    raw_description: Optional[str] = None
    discipline: Optional[str] = None
    extracted_start: Optional[date] = None
    extracted_finish: Optional[date] = None
    progress_pct: Optional[float] = None
    quantity_done: Optional[float] = None
    location_tag: Optional[str] = None
    supervisor_name: Optional[str] = None
    extraction_confidence: Optional[float] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Activity Match
# ---------------------------------------------------------------------------

class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    extracted_event_id: uuid.UUID
    schedule_node_id: Optional[uuid.UUID] = None
    match_score: Optional[float] = None
    match_method: Optional[str] = None
    match_explanation: Optional[str] = None
    status: str
    reviewed_by: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    extracted_event: Optional[ExtractedEventResponse] = None
    schedule_node: Optional[ScheduleNodeResponse] = None


class MatchApproveRequest(BaseModel):
    note: Optional[str] = None


class MatchRejectRequest(BaseModel):
    reason: Optional[str] = None


class BulkApproveRequest(BaseModel):
    match_ids: List[uuid.UUID]


# ---------------------------------------------------------------------------
# Actual Progress
# ---------------------------------------------------------------------------

class ActualProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    schedule_node_id: uuid.UUID
    match_id: Optional[uuid.UUID] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    progress_pct: Optional[float] = None
    is_complete: bool
    confidence_score: Optional[float] = None
    source_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Performance Metric
# ---------------------------------------------------------------------------

class MetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    schedule_node_id: Optional[uuid.UUID] = None
    computed_at: datetime
    spi: Optional[float] = None
    cpi: Optional[float] = None
    float_consumed: Optional[int] = None
    predicted_finish: Optional[date] = None
    delay_risk_score: Optional[float] = None
    forecast_explanation: Optional[str] = None


# ---------------------------------------------------------------------------
# Anomaly Flag
# ---------------------------------------------------------------------------

class AnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    related_event_id: Optional[uuid.UUID] = None
    anomaly_type: str
    description: Optional[str] = None
    severity: str
    status: str
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


# Forward references
ScheduleNodeResponse.model_rebuild()
SubmissionStatus.model_rebuild()
