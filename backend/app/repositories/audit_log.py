"""AuditLog repository with filtering and search support."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditLog)

    async def get_by_entity(self, table_name: str, record_id: str) -> list[AuditLog]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.table_name == table_name,
                self.model.record_id == record_id,
            ).order_by(self.model.performed_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: str) -> list[AuditLog]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.performed_by == user_id
            ).order_by(self.model.performed_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_action(self, action: str) -> list[AuditLog]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.action == action
            ).order_by(self.model.performed_at.desc())
        )
        return list(result.scalars().all())
