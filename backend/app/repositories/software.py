"""Software repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.software import Software
from app.repositories.base import BaseRepository


class SoftwareRepository(BaseRepository[Software]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Software)

    async def is_duplicate_name(self, name: str, exclude_id: str | None = None) -> bool:
        filters = {"name": name}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.name == name:
                return False
        return await self.exists(**filters)
