"""Company CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.common import PaginationParams, build_response
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["master-data"])


@router.get("")
async def list_companies(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = CompanyService(db)
    items, meta = await service.list_companies(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[CompanyResponse.model_validate(c) for c in items],
        pagination=meta,
    )


@router.get("/{company_id}")
async def get_company(
    company_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = CompanyService(db)
    item = await service.get(company_id)
    if not item or item.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")
    return build_response(data=CompanyResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = CompanyService(db)
    item = await service.create_company(body.model_dump(), user_id=str(current_user.id))
    return build_response(
        data=CompanyResponse.model_validate(item),
        message="Company created",
    )


@router.put("/{company_id}")
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = CompanyService(db)
    item = await service.update_company(company_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=CompanyResponse.model_validate(item), message="Company updated")


@router.delete("/{company_id}", status_code=status.HTTP_200_OK)
async def delete_company(
    company_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN))],
):
    service = CompanyService(db)
    await service.delete_company(company_id, user_id=str(current_user.id))
    return build_response(message="Company deleted")
