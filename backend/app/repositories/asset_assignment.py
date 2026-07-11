"""AssetAssignment repository."""

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset_assignment import AssetAssignment
from app.repositories.base import BaseRepository


class AssetAssignmentRepository(BaseRepository[AssetAssignment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AssetAssignment)

    async def get_active_by_asset(self, asset_id: str) -> AssetAssignment | None:
        result = await self.db.execute(
            select(self.model).where(
                self.model.asset_id == asset_id,
                self.model.status == "assigned",
            ).order_by(desc(self.model.assigned_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history_by_asset(self, asset_id: str) -> list[AssetAssignment]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.asset_id == asset_id,
            ).order_by(desc(self.model.assigned_at))
        )
        return list(result.scalars().all())
