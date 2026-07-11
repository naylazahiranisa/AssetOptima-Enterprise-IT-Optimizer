"""Location CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.location import (LocationCreate, LocationResponse,
                                  LocationUpdate)
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.location import LocationService

router = APIRouter(prefix="/locations", tags=["master-data"])


@router.get("")
async def list_locations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = LocationService(db)
    items, meta = await service.list_locations(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[LocationResponse.model_validate(l) for l in items],
        pagination=meta,
    )


@router.get("/{location_id}")
async def get_location(
    location_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = LocationService(db)
    item = await service.get(location_id)
    if not item or item.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Location not found")
    return build_response(data=LocationResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_location(
    body: LocationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = LocationService(db)
    item = await service.create_location(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=LocationResponse.model_validate(item), message="Location created")


@router.put("/{location_id}")
async def update_location(
    location_id: str,
    body: LocationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = LocationService(db)
    item = await service.update_location(location_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=LocationResponse.model_validate(item), message="Location updated")


@router.delete("/{location_id}", status_code=status.HTTP_200_OK)
async def delete_location(
    location_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = LocationService(db)
    await service.delete_location(location_id, user_id=str(current_user.id))
    return build_response(message="Location deleted")
