"""Notification endpoints with unread, read, archive, and delete operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    UnreadCountResponse,
)
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", summary="List notifications")
async def list_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    category: str | None = Query(None, alias="category"),
    priority: str | None = Query(None, alias="priority"),
    status: str | None = Query(None, alias="status"),
):
    filters = {}
    if category:
        filters["category"] = category
    if priority:
        filters["priority"] = priority
    if status:
        filters["status"] = status
    if current_user.role != Role.SUPER_ADMIN:
        filters["user_id"] = str(current_user.id)
    service = NotificationService(db)
    items, meta = await service.list_notifications(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(data=[NotificationResponse.model_validate(n) for n in items], pagination=meta)


@router.get("/unread", summary="Get unread notifications for current user")
async def get_unread(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    items = await service.get_unread(
        user_id=str(current_user.id),
        role=current_user.role.value if current_user.role else None,
    )
    return build_response(data=[NotificationResponse.model_validate(n) for n in items], message="Unread notifications")


@router.get("/unread/count", summary="Count unread notifications")
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    total, by_category = await service.get_unread_count(str(current_user.id))
    return build_response(data=UnreadCountResponse(total=total, by_category=by_category))


@router.get("/{notification_id}", summary="Get notification by ID")
async def get_notification(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    item = await service.get_notification(notification_id)
    return build_response(data=NotificationResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create notification (system/internal use)")
async def create_notification(
    body: NotificationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    data = body.model_dump()
    if not data.get("user_id"):
        data["user_id"] = str(current_user.id)
    item = await service.create_notification(data)
    return build_response(data=NotificationResponse.model_validate(item), message="Notification created")


@router.post("/read/{notification_id}", summary="Mark notification as read")
async def mark_as_read(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    item = await service.mark_as_read(notification_id)
    return build_response(data=NotificationResponse.model_validate(item), message="Notification marked as read")


@router.post("/read-all", summary="Mark all notifications as read")
async def mark_all_as_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    count = await service.mark_all_as_read(str(current_user.id))
    return build_response(data={"marked_read": count}, message=f"{count} notifications marked as read")


@router.post("/archive/{notification_id}", summary="Archive a notification")
async def archive_notification(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = NotificationService(db)
    item = await service.archive(notification_id)
    return build_response(data=NotificationResponse.model_validate(item), message="Notification archived")


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK, summary="Delete an archived notification")
async def delete_notification(
    notification_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN,))],
):
    service = NotificationService(db)
    await service.delete_notification(notification_id)
    return build_response(message="Notification deleted permanently")
