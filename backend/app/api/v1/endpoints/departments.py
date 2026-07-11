"""Department CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.department import (DepartmentCreate, DepartmentResponse,
                                    DepartmentUpdate)
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.department import DepartmentService

router = APIRouter(prefix="/departments", tags=["master-data"])


@router.get("")
async def list_departments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = DepartmentService(db)
    items, meta = await service.list_departments(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[DepartmentResponse.model_validate(d) for d in items],
        pagination=meta,
    )


@router.get("/{department_id}")
async def get_department(
    department_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = DepartmentService(db)
    item = await service.get(department_id)
    if not item or item.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found")
    return build_response(data=DepartmentResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_department(
    body: DepartmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = DepartmentService(db)
    item = await service.create_department(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=DepartmentResponse.model_validate(item), message="Department created")


@router.put("/{department_id}")
async def update_department(
    department_id: str,
    body: DepartmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = DepartmentService(db)
    item = await service.update_department(department_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=DepartmentResponse.model_validate(item), message="Department updated")


@router.delete("/{department_id}", status_code=status.HTTP_200_OK)
async def delete_department(
    department_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = DepartmentService(db)
    await service.delete_department(department_id, user_id=str(current_user.id))
    return build_response(message="Department deleted")
