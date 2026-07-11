"""Employee CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.employee import (EmployeeCreate, EmployeeResponse,
                                  EmployeeUpdate)
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.employee import EmployeeService

router = APIRouter(prefix="/employees", tags=["master-data"])


@router.get("")
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = EmployeeService(db)
    items, meta = await service.list_employees(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[EmployeeResponse.model_validate(e) for e in items],
        pagination=meta,
    )


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = EmployeeService(db)
    item = await service.get(employee_id)
    if not item or item.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return build_response(data=EmployeeResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(
    body: EmployeeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = EmployeeService(db)
    item = await service.create_employee(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=EmployeeResponse.model_validate(item), message="Employee created")


@router.put("/{employee_id}")
async def update_employee(
    employee_id: str,
    body: EmployeeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = EmployeeService(db)
    item = await service.update_employee(employee_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=EmployeeResponse.model_validate(item), message="Employee updated")


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
async def delete_employee(
    employee_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = EmployeeService(db)
    await service.delete_employee(employee_id, user_id=str(current_user.id))
    return build_response(message="Employee deleted")
