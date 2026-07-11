"""AssetHistory repository."""

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset_history import AssetHistory
from app.repositories.base import BaseRepository


class AssetHistoryRepository(BaseRepository[AssetHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AssetHistory)

    async def get_by_asset(self, asset_id: str) -> list[AssetHistory]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.asset_id == asset_id,
            ).order_by(desc(self.model.performed_at))
        )
        return list(result.scalars().all())
