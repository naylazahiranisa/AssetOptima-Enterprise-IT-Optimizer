"""Software Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SoftwareCreate(BaseModel):
    name: str = Field(..., max_length=255)
    vendor_id: str | None = None
    category_id: str | None = None
    current_version: str | None = Field(None, max_length=50)
    license_type: str = Field(default="subscription", max_length=20)
    monthly_cost: float | None = None
    annual_cost: float | None = None
    status: str = Field(default="active", max_length=20)
    description: str | None = Field(None, max_length=2000)


class SoftwareUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    vendor_id: str | None = None
    category_id: str | None = None
    current_version: str | None = Field(None, max_length=50)
    license_type: str | None = Field(None, max_length=20)
    monthly_cost: float | None = None
    annual_cost: float | None = None
    status: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=2000)
    is_active: bool | None = None


class SoftwareResponse(BaseModel):
    id: str
    name: str
    vendor_id: str | None
    category_id: str | None
    current_version: str | None
    license_type: str
    monthly_cost: float | None
    annual_cost: float | None
    status: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
