"""SQLAlchemy ORM models for NEXUS PM."""
import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    supervisor = "supervisor"
    planner = "planner"
    pm = "pm"
    admin = "admin"
    auditor = "auditor"


class ProjectStatus(str, enum.Enum):
    planning = "planning"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class SubmissionType(str, enum.Enum):
    voice = "voice"
    text = "text"
    excel = "excel"
    pdf = "pdf"
    dpr = "dpr"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class MatchStatus(str, enum.Enum):
    auto_accepted = "auto_accepted"
    needs_review = "needs_review"
    flagged_new = "flagged_new"
    rejected = "rejected"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AnomalyStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.supervisor
    )
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # relationships
    project: Mapped["Project | None"] = relationship("Project", foreign_keys=[project_id], back_populates="members")
    submissions: Mapped[list["FieldSubmission"]] = relationship(
        "FieldSubmission", foreign_keys="FieldSubmission.submitted_by", back_populates="submitter"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    client: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    baseline_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    baseline_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"), nullable=False, default=ProjectStatus.active
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    members: Mapped[list["User"]] = relationship(
        "User", foreign_keys="User.project_id", back_populates="project"
    )
    schedule_nodes: Mapped[list["ScheduleNode"]] = relationship(
        "ScheduleNode", back_populates="project", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["FieldSubmission"]] = relationship(
        "FieldSubmission", back_populates="project", cascade="all, delete-orphan"
    )
    metrics: Mapped[list["PerformanceMetric"]] = relationship(
        "PerformanceMetric", back_populates="project", cascade="all, delete-orphan"
    )
    anomalies: Mapped[list["AnomalyFlag"]] = relationship(
        "AnomalyFlag", back_populates="project", cascade="all, delete-orphan"
    )


class ScheduleNode(Base):
    __tablename__ = "schedule_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    activity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("schedule_nodes.id", ondelete="SET NULL"), nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    baseline_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    baseline_finish: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_quantity: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_milestone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    float_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="schedule_nodes")
    parent: Mapped["ScheduleNode | None"] = relationship(
        "ScheduleNode", remote_side="ScheduleNode.id", back_populates="children"
    )
    children: Mapped[list["ScheduleNode"]] = relationship(
        "ScheduleNode", back_populates="parent"
    )
    actuals: Mapped[list["ActualProgress"]] = relationship(
        "ActualProgress", back_populates="schedule_node", cascade="all, delete-orphan"
    )
    matches: Mapped[list["ActivityMatch"]] = relationship(
        "ActivityMatch", back_populates="schedule_node"
    )


class FieldSubmission(Base):
    __tablename__ = "field_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    submission_type: Mapped[SubmissionType] = mapped_column(
        Enum(SubmissionType, name="submission_type"), nullable=False
    )
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status"),
        nullable=False,
        default=ProcessingStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="submissions")
    submitter: Mapped["User"] = relationship(
        "User", foreign_keys=[submitted_by], back_populates="submissions"
    )
    extracted_events: Mapped[list["ExtractedEvent"]] = relationship(
        "ExtractedEvent", back_populates="submission", cascade="all, delete-orphan"
    )


class ExtractedEvent(Base):
    __tablename__ = "extracted_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("field_submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raw_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extracted_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    extracted_finish: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    quantity_done: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    location_tag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supervisor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    submission: Mapped["FieldSubmission"] = relationship(
        "FieldSubmission", back_populates="extracted_events"
    )
    matches: Mapped[list["ActivityMatch"]] = relationship(
        "ActivityMatch", back_populates="extracted_event", cascade="all, delete-orphan"
    )


class ActivityMatch(Base):
    __tablename__ = "activity_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    extracted_event_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("extracted_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_node_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("schedule_nodes.id", ondelete="SET NULL"), nullable=True
    )
    match_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    match_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"), nullable=False, default=MatchStatus.needs_review
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    extracted_event: Mapped["ExtractedEvent"] = relationship(
        "ExtractedEvent", back_populates="matches"
    )
    schedule_node: Mapped["ScheduleNode | None"] = relationship(
        "ScheduleNode", back_populates="matches"
    )
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewed_by])
    actual_progress: Mapped["ActualProgress | None"] = relationship(
        "ActualProgress", back_populates="match", uselist=False
    )


class ActualProgress(Base):
    __tablename__ = "actual_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_node_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("schedule_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("activity_matches.id", ondelete="SET NULL"), nullable=True
    )
    actual_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_finish: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True, default=0)
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audit_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    # relationships
    project: Mapped["Project"] = relationship("Project")
    schedule_node: Mapped["ScheduleNode"] = relationship(
        "ScheduleNode", back_populates="actuals"
    )
    match: Mapped["ActivityMatch | None"] = relationship(
        "ActivityMatch", back_populates="actual_progress"
    )


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_node_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("schedule_nodes.id", ondelete="SET NULL"), nullable=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    spi: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    cpi: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    float_consumed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    predicted_finish: Mapped[date | None] = mapped_column(Date, nullable=True)
    delay_risk_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    forecast_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="metrics")
    schedule_node: Mapped["ScheduleNode | None"] = relationship("ScheduleNode")


class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    related_event_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("extracted_events.id", ondelete="SET NULL"), nullable=True
    )
    anomaly_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="severity"), nullable=False, default=Severity.medium
    )
    status: Mapped[AnomalyStatus] = mapped_column(
        Enum(AnomalyStatus, name="anomaly_status"), nullable=False, default=AnomalyStatus.open
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="anomalies")
    resolver: Mapped["User | None"] = relationship("User", foreign_keys=[resolved_by])


class InstitutionalMemory(Base):
    __tablename__ = "institutional_memory"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    project_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    activity_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    planned_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delay_causes: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    # relationships
    project: Mapped["Project | None"] = relationship("Project")


class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
