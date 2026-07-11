"""Asset Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    asset_code: str = Field(..., max_length=100)
    serial_number: str | None = Field(None, max_length=200)
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=2000)
    category_id: str = Field(...)
    vendor_id: str | None = None
    location_id: str | None = None
    condition: str = Field(default="good", max_length=20)
    purchase_date: str | None = None
    purchase_price: float | None = None
    warranty_expiry: str | None = None
    notes: str | None = Field(None, max_length=2000)


class AssetUpdate(BaseModel):
    asset_code: str | None = Field(None, max_length=100)
    serial_number: str | None = Field(None, max_length=200)
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category_id: str | None = None
    vendor_id: str | None = None
    location_id: str | None = None
    condition: str | None = Field(None, max_length=20)
    status: str | None = Field(None, max_length=20)
    purchase_date: str | None = None
    purchase_price: float | None = None
    warranty_expiry: str | None = None
    notes: str | None = Field(None, max_length=2000)
    is_active: bool | None = None


class AssetResponse(BaseModel):
    id: str
    asset_code: str
    serial_number: str | None
    name: str
    description: str | None
    category_id: str
    vendor_id: str | None
    location_id: str | None
    current_employee_id: str | None
    status: str
    condition: str
    purchase_date: datetime | None
    purchase_price: float | None
    warranty_expiry: datetime | None
    qr_value: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetQRResponse(BaseModel):
    qr_value: str
    asset_code: str
    name: str
    status: str

    model_config = {"from_attributes": True}
