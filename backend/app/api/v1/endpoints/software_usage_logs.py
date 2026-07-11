"""SoftwareUsageLog CRUD and analytics endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.software_usage_log import SoftwareUsageLogCreate, SoftwareUsageLogResponse, SoftwareUsageLogUpdate
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.software_usage_log_service import SoftwareUsageLogService

router = APIRouter(prefix="/software/usage", tags=["software"])


@router.get("/logs", summary="List usage logs")
async def list_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "login_time",
    sort_order: str = "desc",
    employee_id: str | None = Query(None, alias="employee_id"),
    software_id: str | None = Query(None, alias="software_id"),
):
    service = SoftwareUsageLogService(db)
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if software_id:
        filters["software_id"] = software_id
    items, meta = await service.list_logs(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order),
        filters=filters,
    )
    return build_response(data=[SoftwareUsageLogResponse.model_validate(l) for l in items], pagination=meta)


@router.post("/logs", status_code=status.HTTP_201_CREATED, summary="Create usage log entry")
async def create_log(
    body: SoftwareUsageLogCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SoftwareUsageLogService(db)
    item = await service.create_log(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=SoftwareUsageLogResponse.model_validate(item), message="Usage log created")


@router.put("/logs/{log_id}", summary="Update usage log (e.g. set logout_time)")
async def update_log(
    log_id: str,
    body: SoftwareUsageLogUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = SoftwareUsageLogService(db)
    item = await service.update_log(log_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=SoftwareUsageLogResponse.model_validate(item), message="Usage log updated")


@router.get("/top", summary="Top most-used software")
async def top_software(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    limit: int = Query(10, ge=1, le=50),
):
    service = SoftwareUsageLogService(db)
    items = await service.get_top_software(limit)
    return build_response(data=items, message="Top software usage")


@router.get("/inactive", summary="Employees inactive for N days")
async def inactive_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    days: int = Query(30, ge=1, le=365),
):
    service = SoftwareUsageLogService(db)
    items = await service.get_inactive_employees(days)
    return build_response(data=items, message=f"Employees inactive for {days}+ days")
