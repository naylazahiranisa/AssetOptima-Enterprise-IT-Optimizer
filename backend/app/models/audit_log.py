"""AuditLog ORM model.

Records every write operation and authentication event across all
modules for compliance and traceability.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AuditAction:
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN_ASSET = "assign_asset"
    RETURN_ASSET = "return_asset"
    TRANSFER_ASSET = "transfer_asset"
    ASSIGN_LICENSE = "assign_license"
    REMOVE_LICENSE = "remove_license"
    QR_SCAN = "qr_scan"
    AI_CHAT = "ai_chat"
    PREDICTION_REQUEST = "prediction_request"
    SETTINGS_UPDATE = "settings_update"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    table_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    record_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    user_role: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )
