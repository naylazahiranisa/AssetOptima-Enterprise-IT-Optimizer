"""Notification repository with unread, count, and bulk operations."""

from datetime import datetime, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationStatus
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Notification)

    async def get_unread_by_user(self, user_id: str) -> list[Notification]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.status == NotificationStatus.UNREAD,
            ).order_by(desc(self.model.created_at))
        )
        return list(result.scalars().all())

    async def get_unread_by_role(self, role: str) -> list[Notification]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.recipient_role == role,
                self.model.status == NotificationStatus.UNREAD,
            ).order_by(desc(self.model.created_at))
        )
        return list(result.scalars().all())

    async def get_unread_broadcast(self) -> list[Notification]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.is_broadcast == True,
                self.model.status == NotificationStatus.UNREAD,
            ).order_by(desc(self.model.created_at))
        )
        return list(result.scalars().all())

    async def count_unread_by_user(self, user_id: str) -> int:
        counts = await self.db.execute(
            select(self.model.category, func.count()).where(
                self.model.user_id == user_id,
                self.model.status == NotificationStatus.UNREAD,
            ).group_by(self.model.category)
        )
        rows = counts.all()
        total = sum(r[1] for r in rows)
        by_category = {r[0]: r[1] for r in rows}
        return total, by_category

    async def mark_as_read(self, notification_id: str) -> Notification | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == notification_id)
        )
        n = result.scalar_one_or_none()
        if n:
            n.status = NotificationStatus.READ
            n.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.flush()
            await self.db.refresh(n)
        return n

    async def mark_all_as_read(self, user_id: str) -> int:
        result = await self.db.execute(
            select(self.model).where(
                self.model.user_id == user_id,
                self.model.status == NotificationStatus.UNREAD,
            )
        )
        notifications = list(result.scalars().all())
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for n in notifications:
            n.status = NotificationStatus.READ
            n.read_at = now
        await self.db.flush()
        return len(notifications)

    async def archive(self, notification_id: str) -> Notification | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == notification_id)
        )
        n = result.scalar_one_or_none()
        if n:
            n.status = NotificationStatus.ARCHIVED
            await self.db.flush()
            await self.db.refresh(n)
        return n
