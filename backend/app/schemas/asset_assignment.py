"""AssetAssignment Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AssetAssignRequest(BaseModel):
    employee_id: str = Field(...)
    expected_return_date: str | None = None
    notes: str | None = Field(None, max_length=500)


class AssetReturnRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)
    condition: str | None = Field(None, max_length=20)


class AssetTransferRequest(BaseModel):
    employee_id: str = Field(...)
    notes: str | None = Field(None, max_length=500)


class AssetAssignmentResponse(BaseModel):
    id: str
    asset_id: str
    employee_id: str
    assigned_by: str | None
    assigned_at: datetime
    returned_at: datetime | None
    expected_return_date: datetime | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
