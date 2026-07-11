"""NotificationPreference endpoints for managing per-user notification settings."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationPreferenceCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from app.schemas.common import build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.notification_preference_service import NotificationPreferenceService

router = APIRouter(prefix="/notification-preferences", tags=["notifications"])


@router.get("", summary="List notification preferences for current user")
async def list_preferences(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationPreferenceService(db)
    items = await service.get_preferences(str(current_user.id))
    return build_response(data=[NotificationPreferenceResponse.model_validate(p) for p in items])


@router.get("/{category}", summary="Get preference for a specific category")
async def get_preference(
    category: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationPreferenceService(db)
    item = await service.get_preference(str(current_user.id), category)
    return build_response(data=NotificationPreferenceResponse.model_validate(item))


@router.put("/{category}", summary="Create or update notification preference")
async def upsert_preference(
    category: str,
    body: NotificationPreferenceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationPreferenceService(db)
    item = await service.upsert_preference(
        str(current_user.id), category,
        body.model_dump(exclude_unset=True),
    )
    return build_response(data=NotificationPreferenceResponse.model_validate(item), message="Preference updated")


@router.delete("/{category}", status_code=status.HTTP_200_OK, summary="Delete notification preference")
async def delete_preference(
    category: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN,))],
):
    service = NotificationPreferenceService(db)
    await service.delete_preference(str(current_user.id), category)
    return build_response(message="Preference deleted")
