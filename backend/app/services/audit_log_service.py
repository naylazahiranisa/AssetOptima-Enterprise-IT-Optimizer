"""AuditLog service for querying immutable audit records."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log import AuditLogRepository
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditLogRepository(db)

    async def list_audit_logs(self, pagination: PaginationParams, filters: dict | None = None):
        base = {}
        if filters:
            base.update(filters)
        return await self.repo.get_all(pagination, filters=base, search_columns=["table_name", "action", "performed_by"])

    async def get_audit_log(self, record_id: str):
        item = await self.repo.get_by_id(record_id)
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Audit log not found")
        return item

    async def get_by_entity(self, table_name: str, record_id: str):
        return await self.repo.get_by_entity(table_name, record_id)

    async def get_by_user(self, user_id: str):
        return await self.repo.get_by_user(user_id)

    async def get_by_action(self, action: str):
        return await self.repo.get_by_action(action)
