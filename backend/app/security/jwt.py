"""JWT token creation, validation, and decoding.

Supports access tokens (short-lived) and refresh tokens (long-lived).
All tokens include the user's UUID, email, and role in the payload.
"""

import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config.settings import settings

logger = logging.getLogger(__name__)

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _create_token(
    subject: str,
    email: str,
    role: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    """Build and sign a JWT with standard claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, email: str, role: str) -> str:
    """Issue a short-lived access token."""
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, email, role, ACCESS_TOKEN_TYPE, delta)


def create_refresh_token(subject: str, email: str, role: str) -> str:
    """Issue a long-lived refresh token."""
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject, email, role, REFRESH_TOKEN_TYPE, delta)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT.

    Returns the payload dict on success.
    Raises ``JWTError`` on invalid signature, expiry, or malformed token.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
