"""SoftwareCategory Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SoftwareCategoryCreate(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=50)
    description: str | None = Field(None, max_length=1000)


class SoftwareCategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=1000)
    is_active: bool | None = None


class SoftwareCategoryResponse(BaseModel):
    id: str
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
