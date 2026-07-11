"""AssetCategory CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.asset_category import AssetCategoryCreate, AssetCategoryResponse, AssetCategoryUpdate
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.asset_category import AssetCategoryService

router = APIRouter(prefix="/asset-categories", tags=["assets"])


@router.get("",
    summary="List asset categories",
    description="Returns a paginated list of asset categories. Accessible by all authenticated users.")
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = AssetCategoryService(db)
    items, meta = await service.list_categories(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[AssetCategoryResponse.model_validate(c) for c in items],
        pagination=meta,
    )


@router.get("/{category_id}",
    summary="Get asset category by ID",
    description="Returns a single asset category by its UUID.")
async def get_category(
    category_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = AssetCategoryService(db)
    item = await service.get(category_id)
    if not item or item.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset category not found")
    return build_response(data=AssetCategoryResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED,
    summary="Create asset category",
    description="Creates a new asset category. Requires Super Admin or IT Support role.")
async def create_category(
    body: AssetCategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetCategoryService(db)
    item = await service.create_category(body.model_dump(), user_id=str(current_user.id))
    return build_response(
        data=AssetCategoryResponse.model_validate(item),
        message="Asset category created",
    )


@router.put("/{category_id}",
    summary="Update asset category",
    description="Updates an existing asset category. Requires Super Admin or IT Support role.")
async def update_category(
    category_id: str,
    body: AssetCategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetCategoryService(db)
    item = await service.update_category(category_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=AssetCategoryResponse.model_validate(item), message="Asset category updated")


@router.delete("/{category_id}", status_code=status.HTTP_200_OK,
    summary="Delete asset category",
    description="Soft-deletes an asset category. Requires Super Admin or IT Support role.")
async def delete_category(
    category_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetCategoryService(db)
    await service.delete_category(category_id, user_id=str(current_user.id))
    return build_response(message="Asset category deleted")
