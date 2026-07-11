"""Vendor repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.repositories.base import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Vendor)

    async def is_duplicate_code(self, code: str, exclude_id: str | None = None) -> bool:
        filters = {"code": code}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.code == code:
                return False
        return await self.exists(**filters)
