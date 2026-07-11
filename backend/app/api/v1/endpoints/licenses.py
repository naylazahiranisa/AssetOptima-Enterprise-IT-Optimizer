"""License CRUD and special analytics endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.license_schema import LicenseCreate, LicenseResponse, LicenseUpdate
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.license_service import LicenseService

router = APIRouter(prefix="/software/licenses", tags=["software"])


@router.get("", summary="List licenses")
async def list_licenses(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    software_id: str | None = Query(None, alias="software_id"),
    status: str | None = Query(None, alias="status"),
):
    service = LicenseService(db)
    filters = {"is_deleted": False}
    if software_id:
        filters["software_id"] = software_id
    if status:
        filters["status"] = status
    items, meta = await service.list_licenses(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(data=[LicenseResponse.model_validate(l) for l in items], pagination=meta)


@router.get("/expiring", summary="List licenses expiring soon")
async def expiring_licenses(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    days: int = Query(30, ge=1, le=365),
):
    service = LicenseService(db)
    items = await service.get_expiring(days)
    return build_response(data=[LicenseResponse.model_validate(l) for l in items], message=f"Licenses expiring within {days} days")


@router.get("/available", summary="List licenses with available seats")
async def available_seats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    items = await service.get_available_seats()
    return build_response(data=[LicenseResponse.model_validate(l) for l in items], message="Licenses with available seats")


@router.get("/unused", summary="List licenses with zero allocations")
async def unused_licenses(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    items = await service.get_unused_licenses()
    return build_response(data=[LicenseResponse.model_validate(l) for l in items], message="Unused licenses")


@router.get("/cost/summary", summary="Monthly and annual cost summary")
async def cost_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    service = LicenseService(db)
    summary = await service.get_cost_summary()
    return build_response(data=summary, message="Cost summary")


@router.get("/{license_id}", summary="Get license by ID")
async def get_license(
    license_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    item = await service.get(license_id)
    if not item or item.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")
    return build_response(data=LicenseResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create license")
async def create_license(
    body: LicenseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    item = await service.create_license(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=LicenseResponse.model_validate(item), message="License created")


@router.put("/{license_id}", summary="Update license")
async def update_license(
    license_id: str,
    body: LicenseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    item = await service.update_license(license_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=LicenseResponse.model_validate(item), message="License updated")


@router.delete("/{license_id}", status_code=status.HTTP_200_OK, summary="Delete license")
async def delete_license(
    license_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = LicenseService(db)
    await service.delete_license(license_id, user_id=str(current_user.id))
    return build_response(message="License deleted")
