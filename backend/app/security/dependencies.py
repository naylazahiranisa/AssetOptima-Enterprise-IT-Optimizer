"""FastAPI security dependencies.

Provides reusable callables for:
- Extracting the authenticated user from the request
- Validating role-based access
- Checking fine-grained permissions
"""

import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.security.jwt import decode_token
from app.security.permissions import Permission, Role, ROLE_PERMISSIONS

logger = logging.getLogger(__name__)

# Swagger / OpenAPI bearer-token scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Extract and return the authenticated user from the Bearer token.

    Raises ``401 Unauthorized`` if the token is missing, invalid, or
    the user no longer exists.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    return user


def require_roles(*roles: Role) -> Callable:
    """Return a dependency that only allows requests from users with one of the given roles.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))]):
            ...
    """
    allowed = set(roles)

    async def _role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _role_checker


def require_permissions(*permissions: Permission) -> Callable:
    """Return a dependency that checks the current user's role grants all given permissions.

    Usage::

        @router.get("/reports")
        async def reports(
            user: Annotated[User, Depends(require_permissions(Permission.VIEW_REPORTS))],
        ):
            ...
    """
    required = set(permissions)

    async def _perm_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        user_perms = ROLE_PERMISSIONS.get(current_user.role, [])
        if not required.issubset(user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _perm_checker
