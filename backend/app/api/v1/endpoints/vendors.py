"""Vendor CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.vendor import VendorCreate, VendorResponse, VendorUpdate
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.vendor import VendorService

router = APIRouter(prefix="/vendors", tags=["master-data"])


@router.get("")
async def list_vendors(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = VendorService(db)
    items, meta = await service.list_vendors(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[VendorResponse.model_validate(v) for v in items],
        pagination=meta,
    )


@router.get("/{vendor_id}")
async def get_vendor(
    vendor_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = VendorService(db)
    item = await service.get(vendor_id)
    if not item or item.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vendor not found")
    return build_response(data=VendorResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = VendorService(db)
    item = await service.create_vendor(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=VendorResponse.model_validate(item), message="Vendor created")


@router.put("/{vendor_id}")
async def update_vendor(
    vendor_id: str,
    body: VendorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = VendorService(db)
    item = await service.update_vendor(vendor_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=VendorResponse.model_validate(item), message="Vendor updated")


@router.delete("/{vendor_id}", status_code=status.HTTP_200_OK)
async def delete_vendor(
    vendor_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = VendorService(db)
    await service.delete_vendor(vendor_id, user_id=str(current_user.id))
    return build_response(message="Vendor deleted")
