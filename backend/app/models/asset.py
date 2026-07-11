"""Asset ORM model."""

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AssetStatus:
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"
    LOST = "lost"
    RETIRED = "retired"


class AssetCondition:
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    DAMAGED = "damaged"
    BROKEN = "broken"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    asset_code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    serial_number: Mapped[str | None] = mapped_column(
        String(200), unique=True, nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("asset_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_employee_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssetStatus.AVAILABLE, index=True
    )
    condition: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AssetCondition.GOOD
    )

    purchase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    warranty_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    qr_value: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

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
