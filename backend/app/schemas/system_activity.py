"""SystemActivity Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SystemActivityCreate(BaseModel):
    event_type: str = Field(..., max_length=50)
    severity: str = Field(default="info", max_length=10)
    title: str = Field(..., max_length=255)
    message: str | None = None
    service_name: str | None = Field(None, max_length=100)
    component: str | None = Field(None, max_length=100)
    stack_trace: str | None = None
    metadata_json: str | None = None
    ip_address: str | None = Field(None, max_length=45)
    hostname: str | None = Field(None, max_length=255)


class SystemActivityResponse(BaseModel):
    id: str
    event_type: str
    severity: str
    title: str
    message: str | None
    service_name: str | None
    component: str | None
    stack_trace: str | None
    metadata_json: str | None
    ip_address: str | None
    hostname: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
