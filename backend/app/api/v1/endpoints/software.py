"""Software CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.software import SoftwareCreate, SoftwareResponse, SoftwareUpdate
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.software import SoftwareService

router = APIRouter(prefix="/software", tags=["software"])


@router.get("", summary="List software")
async def list_software(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    category_id: str | None = Query(None, alias="category_id"),
    vendor_id: str | None = Query(None, alias="vendor_id"),
    status: str | None = Query(None, alias="status"),
    license_type: str | None = Query(None, alias="license_type"),
):
    service = SoftwareService(db)
    filters = {"is_deleted": False}
    if category_id:
        filters["category_id"] = category_id
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["status"] = status
    if license_type:
        filters["license_type"] = license_type
    items, meta = await service.list_software(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(data=[SoftwareResponse.model_validate(s) for s in items], pagination=meta)


@router.get("/{software_id}", summary="Get software by ID")
async def get_software(
    software_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = SoftwareService(db)
    item = await service.get(software_id)
    if not item or item.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")
    return build_response(data=SoftwareResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create software")
async def create_software(
    body: SoftwareCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SoftwareService(db)
    item = await service.create_software(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=SoftwareResponse.model_validate(item), message="Software created")


@router.put("/{software_id}", summary="Update software")
async def update_software(
    software_id: str,
    body: SoftwareUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SoftwareService(db)
    item = await service.update_software(software_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=SoftwareResponse.model_validate(item), message="Software updated")


@router.delete("/{software_id}", status_code=status.HTTP_200_OK, summary="Delete software")
async def delete_software(
    software_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SoftwareService(db)
    await service.delete_software(software_id, user_id=str(current_user.id))
    return build_response(message="Software deleted")
