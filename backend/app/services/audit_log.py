"""Audit-log service: records write operations for compliance."""

import json
import logging
from datetime import date, datetime, timezone

from fastapi.encoders import jsonable_encoder

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def _serialize(obj: dict | None) -> str | None:
    """Convert a dict to JSON, handling non-serialisable types."""
    if obj is None:
        return None
    return json.dumps(jsonable_encoder(obj))


async def record_audit(
    db: any,
    table_name: str,
    record_id: str,
    action: str,
    performed_by: str | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
) -> None:
    """Persist an audit log entry asynchronously."""
    log = AuditLog(
        table_name=table_name,
        record_id=record_id,
        action=action,
        old_values=_serialize(old_values),
        new_values=_serialize(new_values),
        performed_by=performed_by,
        performed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(log)
    await db.flush()
    logger.info("Audit: %s on %s[%s] by %s", action, table_name, record_id, performed_by)
