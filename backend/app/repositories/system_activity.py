"""SystemActivity repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_activity import SystemActivity
from app.repositories.base import BaseRepository


class SystemActivityRepository(BaseRepository[SystemActivity]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SystemActivity)

    async def get_by_event_type(self, event_type: str) -> list[SystemActivity]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.event_type == event_type
            ).order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 20) -> list[SystemActivity]:
        result = await self.db.execute(
            select(self.model).order_by(self.model.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_errors(self, limit: int = 50) -> list[SystemActivity]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.severity.in_(["error", "critical"])
            ).order_by(self.model.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
