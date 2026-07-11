"""Notification and NotificationPreference Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: str | None = None
    employee_id: str | None = None
    title: str = Field(..., max_length=255)
    message: str = Field(...)
    category: str = Field(default="system", max_length=30)
    priority: str = Field(default="medium", max_length=10)
    recipient_role: str | None = Field(None, max_length=30)
    reference_id: str | None = Field(None, max_length=100)
    source: str | None = Field(None, max_length=50)
    tenant_id: str | None = None
    is_broadcast: bool = False


class NotificationUpdate(BaseModel):
    status: str | None = Field(None, max_length=10)


class NotificationResponse(BaseModel):
    id: str
    user_id: str | None
    employee_id: str | None
    title: str
    message: str
    category: str
    priority: str
    status: str
    recipient_role: str | None
    reference_id: str | None
    source: str | None
    tenant_id: str | None
    is_broadcast: bool
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationPreferenceCreate(BaseModel):
    category: str = Field(..., max_length=30)
    email_enabled: bool = True
    push_enabled: bool = True
    slack_enabled: bool = False
    teams_enabled: bool = False
    min_priority: str = Field(default="medium", max_length=10)


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    slack_enabled: bool | None = None
    teams_enabled: bool | None = None
    min_priority: str | None = Field(None, max_length=10)


class NotificationPreferenceResponse(BaseModel):
    id: str
    user_id: str
    category: str
    email_enabled: bool
    push_enabled: bool
    slack_enabled: bool
    teams_enabled: bool
    min_priority: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    total: int
    by_category: dict = {}
