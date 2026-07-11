"""Company repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Company)

    async def is_duplicate_code(self, code: str, exclude_id: str | None = None) -> bool:
        """Check whether the given company code already exists."""
        filters = {"code": code}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.code == code:
                return False
        return await self.exists(**filters)
