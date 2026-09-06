"""Audit trail service."""
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditTrail


async def log_action(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    action: str,
    entity: str,
    entity_id: Optional[uuid.UUID] = None,
    old_value: Optional[dict[str, Any]] = None,
    new_value: Optional[dict[str, Any]] = None,
    ip: Optional[str] = None,
) -> AuditTrail:
    """
    Persist an audit trail entry.

    Args:
        db:        Async SQLAlchemy session.
        user_id:   UUID of the acting user (None for system actions).
        action:    Short verb, e.g. 'create', 'approve_match', 'login'.
        entity:    Table / domain object name, e.g. 'project', 'activity_match'.
        entity_id: Primary key of the affected record.
        old_value: JSON-serialisable snapshot before change.
        new_value: JSON-serialisable snapshot after change.
        ip:        Client IP address from the request.

    Returns:
        The persisted AuditTrail ORM object.
    """
    entry = AuditTrail(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip,
    )
    db.add(entry)
    # Note: do NOT commit here – caller controls transaction boundary
    return entry
