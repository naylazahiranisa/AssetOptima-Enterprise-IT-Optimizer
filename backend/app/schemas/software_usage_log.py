"""SoftwareUsageLog Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SoftwareUsageLogCreate(BaseModel):
    employee_id: str = Field(...)
    software_id: str = Field(...)
    login_time: str = Field(...)
    logout_time: str | None = None
    session_duration_seconds: int | None = None
    ip_address: str | None = Field(None, max_length=45)
    os: str | None = Field(None, max_length=100)
    device_name: str | None = Field(None, max_length=255)
    department_id: str | None = None


class SoftwareUsageLogUpdate(BaseModel):
    logout_time: str | None = None
    session_duration_seconds: int | None = None


class SoftwareUsageLogResponse(BaseModel):
    id: str
    employee_id: str
    software_id: str
    login_time: datetime
    logout_time: datetime | None
    session_duration_seconds: int | None
    ip_address: str | None
    os: str | None
    device_name: str | None
    department_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CostSummaryResponse(BaseModel):
    total_monthly_cost: float = 0
    total_annual_cost: float = 0
    department_breakdown: dict = {}


class TopSoftwareResponse(BaseModel):
    software_id: str
    software_name: str
    usage_count: int
    total_duration_seconds: int


class InactiveEmployeeResponse(BaseModel):
    employee_id: str
    employee_name: str
    days_inactive: int
    last_login: datetime | None
