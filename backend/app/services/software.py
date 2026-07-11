"""Software service."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.software import SoftwareRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class SoftwareService(BaseService[SoftwareRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(SoftwareRepository(db), db, "software")

    async def list_software(self, pagination: PaginationParams, filters: dict | None = None):
        base = {"is_deleted": False}
        if filters:
            base.update(filters)
        return await self.list(pagination, filters=base, search_columns=["name", "current_version"])

    async def create_software(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_name(data.get("name", "")):
            raise HTTPException(status.HTTP_409_CONFLICT, f"Software name '{data['name']}' already exists")
        return await self.create(data, user_id)

    async def update_software(self, record_id: str, data: dict, user_id: str | None = None):
        if "name" in data and data["name"]:
            if await self.repo.is_duplicate_name(data["name"], exclude_id=record_id):
                raise HTTPException(status.HTTP_409_CONFLICT, f"Software name '{data['name']}' already exists")
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")

    async def delete_software(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")
