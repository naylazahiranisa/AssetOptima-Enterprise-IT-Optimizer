"""Role (DB model) CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["master-data"])


@router.get("")
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = RoleService(db)
    items, meta = await service.list_roles(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[RoleResponse.model_validate(r) for r in items],
        pagination=meta,
    )


@router.get("/{role_id}")
async def get_role(
    role_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = RoleService(db)
    item = await service.get(role_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return build_response(data=RoleResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = RoleService(db)
    item = await service.create_role(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=RoleResponse.model_validate(item), message="Role created")


@router.put("/{role_id}")
async def update_role(
    role_id: str,
    body: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = RoleService(db)
    item = await service.update_role(role_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=RoleResponse.model_validate(item), message="Role updated")


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = RoleService(db)
    await service.delete_role(role_id, user_id=str(current_user.id))
    return build_response(message="Role deleted")
