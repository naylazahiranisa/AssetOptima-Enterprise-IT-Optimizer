"""EmployeeSoftware Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class EmployeeSoftwareAssignRequest(BaseModel):
    employee_id: str = Field(...)
    software_id: str = Field(...)
    license_id: str | None = None
    notes: str | None = Field(None, max_length=500)


class EmployeeSoftwareRemoveRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)


class EmployeeSoftwareTransferRequest(BaseModel):
    from_employee_id: str = Field(...)
    to_employee_id: str = Field(...)
    software_id: str = Field(...)
    notes: str | None = Field(None, max_length=500)


class EmployeeSoftwareResponse(BaseModel):
    id: str
    employee_id: str
    software_id: str
    license_id: str | None
    assigned_by: str | None
    assigned_at: datetime
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
