"""User CRUD endpoints (admin management of system users)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["master-data"])


@router.get("")
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = UserService(db)
    items, meta = await service.list_users(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[UserResponse.model_validate(u) for u in items],
        pagination=meta,
    )


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = UserService(db)
    item = await service.get(user_id)
    if not item or item.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return build_response(data=UserResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = UserService(db)
    item = await service.create_user(body.model_dump(), user_id=str(current_user.id))
    return build_response(data=UserResponse.model_validate(item), message="User created")


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = UserService(db)
    item = await service.update_user(user_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=UserResponse.model_validate(item), message="User updated")


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = UserService(db)
    await service.delete_user(user_id, user_id=str(current_user.id))
    return build_response(message="User deleted")
