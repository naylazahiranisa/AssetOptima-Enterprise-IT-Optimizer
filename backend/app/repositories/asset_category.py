"""AssetCategory repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset_category import AssetCategory
from app.repositories.base import BaseRepository


class AssetCategoryRepository(BaseRepository[AssetCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AssetCategory)

    async def is_duplicate_code(self, code: str, exclude_id: str | None = None) -> bool:
        filters = {"code": code}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.code == code:
                return False
        return await self.exists(**filters)
