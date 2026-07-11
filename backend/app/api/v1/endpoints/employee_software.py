"""EmployeeSoftware (assign/remove/transfer) endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.employee_software import (
    EmployeeSoftwareAssignRequest,
    EmployeeSoftwareRemoveRequest,
    EmployeeSoftwareResponse,
    EmployeeSoftwareTransferRequest,
)
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.employee_software_service import EmployeeSoftwareService

router = APIRouter(prefix="/software/assignments", tags=["software"])


@router.get("", summary="List software assignments")
async def list_assignments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    employee_id: str | None = Query(None, alias="employee_id"),
    software_id: str | None = Query(None, alias="software_id"),
):
    filters = {}
    if employee_id:
        filters["employee_id"] = employee_id
    if software_id:
        filters["software_id"] = software_id
    service = EmployeeSoftwareService(db)
    items, meta = await service.list_assignments(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order),
        filters=filters,
    )
    return build_response(data=[EmployeeSoftwareResponse.model_validate(a) for a in items], pagination=meta)


@router.post("/assign", status_code=status.HTTP_200_OK, summary="Assign software to employee")
async def assign_software(
    body: EmployeeSoftwareAssignRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = EmployeeSoftwareService(db)
    assignment = await service.assign_software(
        employee_id=body.employee_id,
        software_id=body.software_id,
        license_id=body.license_id,
        assigned_by=str(current_user.id),
        notes=body.notes,
    )
    return build_response(data=EmployeeSoftwareResponse.model_validate(assignment), message="Software assigned")


@router.post("/remove/{assignment_id}", status_code=status.HTTP_200_OK, summary="Remove software from employee")
async def remove_software(
    assignment_id: str,
    body: EmployeeSoftwareRemoveRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = EmployeeSoftwareService(db)
    assignment = await service.remove_software(
        record_id=assignment_id,
        user_id=str(current_user.id),
        notes=body.notes,
    )
    return build_response(data=EmployeeSoftwareResponse.model_validate(assignment), message="Software removed")


@router.post("/transfer", status_code=status.HTTP_200_OK, summary="Transfer software between employees")
async def transfer_software(
    body: EmployeeSoftwareTransferRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = EmployeeSoftwareService(db)
    assignment = await service.transfer_software(
        from_employee_id=body.from_employee_id,
        to_employee_id=body.to_employee_id,
        software_id=body.software_id,
        user_id=str(current_user.id),
        notes=body.notes,
    )
    return build_response(data=EmployeeSoftwareResponse.model_validate(assignment), message="Software transferred")
