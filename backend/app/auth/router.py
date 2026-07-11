"""Authentication endpoints: login, refresh, logout."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    LoginRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
    UserResponse,
)
from app.auth.service import (
    authenticate_user,
    refresh_access_token,
    revoke_refresh_token,
)
from app.database.session import get_db
from app.security.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate with email and password.

    Returns a Bearer access token + refresh token pair.
    """
    try:
        return await authenticate_user(db, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a valid refresh token for a new access token.

    The old refresh token is rotated (revoked and replaced).
    """
    try:
        return await refresh_access_token(db, request.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Revoke the provided refresh token.

    Client should also discard the access token on its side.
    """
    await revoke_refresh_token(db, request.refresh_token)
    return LogoutResponse()


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the profile of the currently authenticated user."""
    return current_user
