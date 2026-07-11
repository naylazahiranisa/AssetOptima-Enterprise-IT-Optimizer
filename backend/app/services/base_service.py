"""Generic base service providing common CRUD orchestration."""

import logging
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.schemas.common import PaginationMeta, PaginationParams
from app.services.audit_log import record_audit

logger = logging.getLogger(__name__)

RepoType = TypeVar("RepoType", bound=BaseRepository)


class BaseService(Generic[RepoType]):
    """Wraps a repository and adds audit logging for every write operation."""

    def __init__(self, repo: RepoType, db: AsyncSession, table_name: str):
        self.repo = repo
        self.db = db
        self.table_name = table_name

    async def list(
        self,
        pagination: PaginationParams,
        filters: dict | None = None,
        search_columns: list[str] | None = None,
    ) -> tuple[list[Any], PaginationMeta]:
        return await self.repo.get_all(pagination, filters, search_columns)

    async def get(self, record_id: str) -> Any | None:
        return await self.repo.get_by_id(record_id)

    async def create(self, data: dict, user_id: str | None = None) -> Any:
        instance = await self.repo.create(**data)
        await record_audit(
            self.db, self.table_name, instance.id, "CREATE", performed_by=user_id, new_values=data
        )
        logger.info("Created %s[%s]", self.table_name, instance.id)
        return instance

    async def update(
        self, record_id: str, data: dict, user_id: str | None = None
    ) -> Any:
        instance = await self.repo.get_by_id(record_id)
        if not instance:
            raise ValueError(f"{self.table_name} not found")

        old = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        instance = await self.repo.update(instance, **data)

        await record_audit(
            self.db, self.table_name, record_id, "UPDATE",
            performed_by=user_id, old_values=old, new_values=data,
        )
        logger.info("Updated %s[%s]", self.table_name, record_id)
        return instance

    async def delete(self, record_id: str, user_id: str | None = None) -> None:
        instance = await self.repo.get_by_id(record_id)
        if not instance:
            raise ValueError(f"{self.table_name} not found")

        old = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        await self.repo.soft_delete(instance)

        await record_audit(
            self.db, self.table_name, record_id, "DELETE",
            performed_by=user_id, old_values=old,
        )
        logger.info("Deleted %s[%s]", self.table_name, record_id)
