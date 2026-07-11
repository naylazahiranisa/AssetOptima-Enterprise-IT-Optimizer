"""EmployeeSoftware (assignment) ORM model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EmployeeSoftwareStatus:
    ACTIVE = "active"
    REMOVED = "removed"
    TRANSFERRED = "transferred"


class EmployeeSoftware(Base):
    __tablename__ = "employee_software"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    software_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("software.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    license_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("licenses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EmployeeSoftwareStatus.ACTIVE
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
