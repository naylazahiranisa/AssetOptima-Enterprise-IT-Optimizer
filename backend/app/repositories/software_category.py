"""SoftwareCategory repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.software_category import SoftwareCategory
from app.repositories.base import BaseRepository


class SoftwareCategoryRepository(BaseRepository[SoftwareCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SoftwareCategory)

    async def is_duplicate_code(self, code: str, exclude_id: str | None = None) -> bool:
        filters = {"code": code}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.code == code:
                return False
        return await self.exists(**filters)

    async def is_duplicate_name(self, name: str, exclude_id: str | None = None) -> bool:
        filters = {"name": name}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.name == name:
                return False
        return await self.exists(**filters)
