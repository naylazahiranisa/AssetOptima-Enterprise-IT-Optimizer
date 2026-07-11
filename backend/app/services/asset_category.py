"""AssetCategory service."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asset_category import AssetCategoryRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class AssetCategoryService(BaseService[AssetCategoryRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssetCategoryRepository(db), db, "asset_categories")

    async def list_categories(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            filters={"is_deleted": False},
            search_columns=["name", "code"],
        )

    async def create_category(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_code(data.get("code", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset category code '{data['code']}' already exists",
            )
        return await self.create(data, user_id)

    async def update_category(self, record_id: str, data: dict, user_id: str | None = None):
        if "code" in data and data["code"]:
            if await self.repo.is_duplicate_code(data["code"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Asset category code '{data['code']}' already exists",
                )
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset category not found")

    async def delete_category(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset category not found")
