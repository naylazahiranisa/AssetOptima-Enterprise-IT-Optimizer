"""Authentication business logic: login, refresh, logout, and seeding.

All database interactions go through SQLAlchemy async sessions.
"""

import hashlib
import logging
from datetime import datetime, timezone

from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, TokenResponse
from app.config.settings import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.security.password import hash_password, verify_password
from app.security.permissions import Role, ROLE_DISPLAY_NAMES

logger = logging.getLogger(__name__)


async def authenticate_user(db: AsyncSession, request: LoginRequest) -> TokenResponse:
    """Validate credentials and return JWT token pair.

    Raises ``ValueError`` on invalid email or password.
    """
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(request.password, user.hashed_password):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("Account is deactivated")

    return await _issue_tokens(db, user)


async def _issue_tokens(db: AsyncSession, user: User) -> TokenResponse:
    """Create access + refresh tokens and persist the refresh token."""
    access = create_access_token(
        subject=str(user.id),
        email=user.email,
        role=user.role.value,
    )
    refresh = create_refresh_token(
        subject=str(user.id),
        email=user.email,
        role=user.role.value,
    )

    # Store hashed refresh token in the database for future revocation
    db_refresh = RefreshToken(
        user_id=user.id,
        token_hash=_hash_token(refresh),
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
        + __import__("datetime").timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_refresh)
    await db.commit()

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=ROLE_DISPLAY_NAMES.get(user.role, user.role.value),
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
    """Validate a refresh token and issue a new access token.

    Returns a dict with ``access_token``, ``token_type``, and ``expires_in``.
    """
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise ValueError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token")

    token_hash = _hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > datetime.now(timezone.utc).replace(tzinfo=None),
        )
    )
    stored = result.scalar_one_or_none()

    if stored is None:
        raise ValueError("Refresh token has been revoked or does not exist")

    # Fetch user to confirm they still exist and are active
    user_result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise ValueError("User not found or deactivated")

    # Rotate: delete old refresh token, issue new one
    await db.delete(stored)
    await db.commit()

    new_refresh = await _issue_tokens(db, user)

    return {
        "access_token": new_refresh.access_token,
        "refresh_token": new_refresh.refresh_token,
        "token_type": "Bearer",
        "expires_in": new_refresh.expires_in,
    }


async def revoke_refresh_token(db: AsyncSession, refresh_token: str) -> None:
    """Delete a refresh token from the database (logout)."""
    token_hash = _hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()
    if stored is not None:
        await db.delete(stored)
        await db.commit()


async def seed_super_admin(db: AsyncSession) -> None:
    """Create the default Super Admin user if no users exist."""
    result = await db.execute(select(User).limit(1))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return

    admin_email = "admin@assetoptima.com"
    admin_password = "Admin@12345"

    admin = User(
        email=admin_email,
        hashed_password=hash_password(admin_password),
        full_name="Super Admin",
        role=Role.SUPER_ADMIN,
        is_active=True,
    )
    db.add(admin)
    await db.commit()

    logger.info("=" * 60)
    logger.info("  DEFAULT SUPER ADMIN CREATED")
    logger.info("  Email    : %s", admin_email)
    logger.info("  Password : %s", admin_password)
    logger.info("  Role     : Super Admin")
    logger.info("  ** CHANGE THIS PASSWORD IN PRODUCTION **")
    logger.info("=" * 60)


def _hash_token(token: str) -> str:
    """Return a SHA-256 hex digest of the token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()
