"""Employee Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., max_length=50)
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    position: str | None = Field(None, max_length=200)
    department_id: str | None = None
    company_id: str | None = None


class EmployeeUpdate(BaseModel):
    employee_id: str | None = Field(None, max_length=50)
    full_name: str | None = Field(None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    position: str | None = Field(None, max_length=200)
    department_id: str | None = None
    company_id: str | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    phone: str | None
    position: str | None
    department_id: str | None
    company_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
