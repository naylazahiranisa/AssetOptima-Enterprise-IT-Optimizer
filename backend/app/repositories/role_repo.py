"""Role (DB model) repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_model import RoleModel
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, RoleModel)

    async def is_duplicate_name(self, name: str, exclude_id: str | None = None) -> bool:
        filters = {"name": name}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.name == name:
                return False
        return await self.exists(**filters)
