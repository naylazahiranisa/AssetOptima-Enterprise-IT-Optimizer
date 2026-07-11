"""SystemActivity ORM model.

Stores system-level events such as application start/stop,
database connectivity changes, API errors, and unhandled exceptions.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SystemEventType:
    APPLICATION_STARTED = "application_started"
    APPLICATION_STOPPED = "application_stopped"
    DATABASE_CONNECTED = "database_connected"
    DATABASE_FAILED = "database_failed"
    API_ERROR = "api_error"
    UNHANDLED_EXCEPTION = "unhandled_exception"


class SystemEventSeverity:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemActivity(Base):
    __tablename__ = "system_activities"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(10), nullable=False, default=SystemEventSeverity.INFO, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    component: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )
