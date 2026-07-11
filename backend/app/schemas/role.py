"""Role (DB model) Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
