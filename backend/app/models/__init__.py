"""
models/__init__.py – import all models so that Base.metadata is fully populated.
"""
from app.models.models import (  # noqa: F401
    ActivityMatch,
    ActualProgress,
    AnomalyFlag,
    AuditTrail,
    ExtractedEvent,
    FieldSubmission,
    InstitutionalMemory,
    PerformanceMetric,
    Project,
    ScheduleNode,
    User,
)
