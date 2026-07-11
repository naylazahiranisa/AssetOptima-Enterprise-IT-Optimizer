"""Role (DB model) service."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.role_repo import RoleRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams


class RoleService(BaseService[RoleRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(RoleRepository(db), db, "roles")

    async def list_roles(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            search_columns=["name", "description"],
        )

    async def create_role(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_name(data.get("name", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role name '{data['name']}' already exists",
            )
        return await self.create(data, user_id)

    async def update_role(self, record_id: str, data: dict, user_id: str | None = None):
        if "name" in data and data["name"]:
            if await self.repo.is_duplicate_name(data["name"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Role name '{data['name']}' already exists",
                )
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")

    async def delete_role(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
