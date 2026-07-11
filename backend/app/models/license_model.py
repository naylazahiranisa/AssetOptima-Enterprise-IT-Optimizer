"""License ORM model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LicenseStatus:
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING_RENEWAL = "pending_renewal"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    license_key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    software_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("software.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    purchase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    renewal_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=LicenseStatus.ACTIVE, index=True
    )
    max_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    allocated_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
