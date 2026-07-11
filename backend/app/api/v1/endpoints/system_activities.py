"""SystemActivity endpoints for monitoring system-level events."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.system_activity import SystemActivityCreate, SystemActivityResponse
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.system_activity_service import SystemActivityService

router = APIRouter(prefix="/system-activities", tags=["system"])


@router.get("", summary="List system activities")
async def list_activities(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    event_type: str | None = Query(None, alias="event_type"),
    severity: str | None = Query(None, alias="severity"),
):
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if severity:
        filters["severity"] = severity
    service = SystemActivityService(db)
    items, meta = await service.list_activities(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(data=[SystemActivityResponse.model_validate(a) for a in items], pagination=meta)


@router.get("/recent", summary="Get recent system activities")
async def get_recent(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
    limit: int = Query(20, ge=1, le=100),
):
    service = SystemActivityService(db)
    items = await service.get_recent(limit)
    return build_response(data=[SystemActivityResponse.model_validate(a) for a in items])


@router.get("/errors", summary="Get recent errors and critical events")
async def get_errors(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
    limit: int = Query(50, ge=1, le=200),
):
    service = SystemActivityService(db)
    items = await service.get_errors(limit)
    return build_response(data=[SystemActivityResponse.model_validate(a) for a in items])


@router.get("/{activity_id}", summary="Get system activity by ID")
async def get_activity(
    activity_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    service = SystemActivityService(db)
    item = await service.get_activity(activity_id)
    return build_response(data=SystemActivityResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create system activity (internal use)")
async def create_activity(
    body: SystemActivityCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SystemActivityService(db)
    item = await service.create_activity(body.model_dump())
    return build_response(data=SystemActivityResponse.model_validate(item), message="System activity recorded")
