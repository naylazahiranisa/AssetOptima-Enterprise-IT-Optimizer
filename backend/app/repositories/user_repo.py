"""User repository (for CRUD operations on the auth User model)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def is_duplicate_email(self, email: str, exclude_id: str | None = None) -> bool:
        filters = {"email": email}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.email == email:
                return False
        return await self.exists(**filters)

    async def get_by_email(self, email: str) -> User | None:
        from sqlalchemy import select

        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
