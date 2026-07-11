"""AuditLog Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: str
    table_name: str
    record_id: str
    action: str
    old_values: str | None
    new_values: str | None
    performed_by: str | None
    user_role: str | None
    ip_address: str | None
    user_agent: str | None
    performed_at: datetime

    model_config = {"from_attributes": True}
