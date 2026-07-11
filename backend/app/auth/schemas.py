"""Pydantic v2 request/response models for authentication endpoints."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login credentials supplied by the client."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Successful authentication response with JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    role: str


class RefreshRequest(BaseModel):
    """Refresh-token request body."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response containing new access and refresh tokens (token rotation)."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    """Logout acknowledgement."""

    message: str = "Successfully logged out"


class UserResponse(BaseModel):
    """Public user profile — never exposes password or sensitive fields."""

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
