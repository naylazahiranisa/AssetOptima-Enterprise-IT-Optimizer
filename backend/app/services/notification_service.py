"""Notification service with unread, read, archive, and broadcast logic."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import NotificationStatus
from app.repositories.notification import NotificationRepository
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationRepository(db)

    async def list_notifications(self, pagination: PaginationParams, filters: dict | None = None):
        base = {}
        if filters:
            base.update(filters)
        return await self.repo.get_all(pagination, filters=base, search_columns=["title", "message"])

    async def get_notification(self, record_id: str):
        item = await self.repo.get_by_id(record_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return item

    async def create_notification(self, data: dict):
        return await self.repo.create(**data)

    async def get_unread(self, user_id: str | None = None, role: str | None = None):
        items = []
        if user_id:
            items = await self.repo.get_unread_by_user(user_id)
        if role:
            items += await self.repo.get_unread_by_role(role)
        items += await self.repo.get_unread_broadcast()
        seen = set()
        unique = []
        for n in items:
            if n.id not in seen:
                seen.add(n.id)
                unique.append(n)
        unique.sort(key=lambda x: x.created_at, reverse=True)
        return unique

    async def get_unread_count(self, user_id: str):
        total, by_category = await self.repo.count_unread_by_user(user_id)
        broadcast = await self.repo.get_unread_broadcast()
        total += len(broadcast)
        for n in broadcast:
            cat = n.category
            by_category[cat] = by_category.get(cat, 0) + 1
        return total, by_category

    async def mark_as_read(self, notification_id: str):
        n = await self.repo.mark_as_read(notification_id)
        if not n:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return n

    async def mark_all_as_read(self, user_id: str):
        count = await self.repo.mark_all_as_read(user_id)
        return count

    async def archive(self, notification_id: str):
        n = await self.repo.archive(notification_id)
        if not n:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        return n

    async def delete_notification(self, record_id: str):
        n = await self.repo.get_by_id(record_id)
        if not n:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        if n.status != NotificationStatus.ARCHIVED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only archived notifications can be deleted")
        await self.repo.hard_delete(n)
