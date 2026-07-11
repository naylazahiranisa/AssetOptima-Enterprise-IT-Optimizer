"""NotificationPreference service."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_preference import NotificationPreferenceRepository

logger = logging.getLogger(__name__)


class NotificationPreferenceService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationPreferenceRepository(db)

    async def get_preferences(self, user_id: str):
        prefs = await self.repo.get_all_by_user(user_id)
        return prefs

    async def get_preference(self, user_id: str, category: str):
        pref = await self.repo.get_by_user_and_category(user_id, category)
        if not pref:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Preference not found for this category")
        return pref

    async def upsert_preference(self, user_id: str, category: str, data: dict):
        existing = await self.repo.get_by_user_and_category(user_id, category)
        if existing:
            for key, value in data.items():
                if value is not None and hasattr(existing, key):
                    setattr(existing, key, value)
            await self.repo.db.flush()
            await self.repo.db.refresh(existing)
            return existing
        data["user_id"] = user_id
        data["category"] = category
        return await self.repo.create(**data)

    async def delete_preference(self, user_id: str, category: str):
        pref = await self.repo.get_by_user_and_category(user_id, category)
        if not pref:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Preference not found")
        await self.repo.hard_delete(pref)
