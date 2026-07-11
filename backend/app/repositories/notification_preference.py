"""NotificationPreference repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationPreference
from app.repositories.base import BaseRepository


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, NotificationPreference)

    async def get_by_user_and_category(self, user_id: str, category: str) -> NotificationPreference | None:
        result = await self.db.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.category == category,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: str) -> list[NotificationPreference]:
        result = await self.db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())
