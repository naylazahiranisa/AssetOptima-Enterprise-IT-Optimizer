"""SystemActivity service for recording and querying system-level events."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.system_activity import SystemActivityRepository
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class SystemActivityService:
    def __init__(self, db: AsyncSession):
        self.repo = SystemActivityRepository(db)

    async def list_activities(self, pagination: PaginationParams, filters: dict | None = None):
        base = {}
        if filters:
            base.update(filters)
        return await self.repo.get_all(pagination, filters=base, search_columns=["title", "event_type", "service_name"])

    async def get_activity(self, record_id: str):
        item = await self.repo.get_by_id(record_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "System activity not found")
        return item

    async def create_activity(self, data: dict):
        return await self.repo.create(**data)

    async def get_recent(self, limit: int = 20):
        return await self.repo.get_recent(limit)

    async def get_errors(self, limit: int = 50):
        return await self.repo.get_errors(limit)
