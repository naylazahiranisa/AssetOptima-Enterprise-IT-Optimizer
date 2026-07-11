"""License Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class LicenseCreate(BaseModel):
    license_key: str = Field(..., max_length=255)
    software_id: str = Field(...)
    purchase_date: str | None = None
    renewal_date: str | None = None
    expiry_date: str | None = None
    status: str = Field(default="active", max_length=20)
    max_seats: int = Field(default=1, ge=1)
    monthly_cost: float | None = None
    annual_cost: float | None = None
    notes: str | None = Field(None, max_length=2000)


class LicenseUpdate(BaseModel):
    license_key: str | None = Field(None, max_length=255)
    software_id: str | None = None
    purchase_date: str | None = None
    renewal_date: str | None = None
    expiry_date: str | None = None
    status: str | None = Field(None, max_length=20)
    max_seats: int | None = Field(None, ge=1)
    monthly_cost: float | None = None
    annual_cost: float | None = None
    notes: str | None = Field(None, max_length=2000)
    is_active: bool | None = None


class LicenseResponse(BaseModel):
    id: str
    license_key: str
    software_id: str
    purchase_date: datetime | None
    renewal_date: datetime | None
    expiry_date: datetime | None
    status: str
    max_seats: int
    allocated_seats: int
    monthly_cost: float | None
    annual_cost: float | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
