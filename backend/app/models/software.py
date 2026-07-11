"""Software ORM model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class LicenseType:
    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    SAAS = "saas"
    OPEN_SOURCE = "open_source"
    FREEWARE = "freeware"


class SoftwareStatus:
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class Software(Base):
    __tablename__ = "software"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    vendor_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("software_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    license_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=LicenseType.SUBSCRIPTION
    )
    monthly_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SoftwareStatus.ACTIVE, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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
