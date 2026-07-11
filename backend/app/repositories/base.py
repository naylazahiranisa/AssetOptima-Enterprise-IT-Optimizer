"""Base repository providing common CRUD, pagination, and soft-delete logic.

All domain-specific repositories inherit from this class to avoid
duplicating standard data-access patterns.
"""

import math
from typing import Any, Generic, TypeVar

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import PaginationMeta, PaginationParams

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Generic repository with standard CRUD and pagination support."""

    def __init__(self, db: AsyncSession, model: type[ModelT]):
        self.db = db
        self.model = model

    async def get_all(
        self,
        pagination: PaginationParams,
        filters: dict | None = None,
        search_columns: list[str] | None = None,
    ) -> tuple[list[ModelT], PaginationMeta]:
        """Paginated list with optional filtering and keyword search."""
        query = select(self.model)

        if filters:
            for col, val in filters.items():
                if hasattr(self.model, col) and val is not None:
                    query = query.where(getattr(self.model, col) == val)

        if pagination.keyword and search_columns:
            conditions = [
                getattr(self.model, col).ilike(f"%{pagination.keyword}%")
                for col in search_columns
                if hasattr(self.model, col)
            ]
            if conditions:
                query = query.where(or_(*conditions))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        default_sort_col = getattr(self.model, "created_at",
                            getattr(self.model, "performed_at",
                            getattr(self.model, "updated_at", None)))
        sort_col = getattr(self.model, pagination.sort_by, default_sort_col)
        if sort_col is None:
            sort_col = self.model.id
        sort_fn = sort_col.desc if pagination.sort_order == "desc" else sort_col.asc
        query = query.order_by(sort_fn())

        offset = (pagination.page - 1) * pagination.per_page
        query = query.offset(offset).limit(pagination.per_page)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        meta = PaginationMeta(
            page=pagination.page,
            per_page=pagination.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / pagination.per_page)),
        )
        return items, meta

    async def get_by_id(self, record_id: str) -> ModelT | None:
        """Fetch a single record by primary key."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> ModelT:
        """Insert a new record and flush."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **kwargs: Any) -> ModelT:
        """Patch an existing record with the given kwargs."""
        for key, value in kwargs.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def soft_delete(self, instance: ModelT) -> None:
        """Set is_deleted = True and record the timestamp."""
        if hasattr(instance, "is_deleted"):
            from datetime import datetime, timezone

            setattr(instance, "is_deleted", True)
            setattr(
                instance,
                "deleted_at",
                datetime.now(timezone.utc).replace(tzinfo=None),
            )
            await self.db.flush()

    async def hard_delete(self, instance: ModelT) -> None:
        """Permanently remove the record from the database."""
        await self.db.delete(instance)
        await self.db.flush()

    async def exists(self, **filters: Any) -> bool:
        """Check whether at least one record matches the given filters."""
        query = select(self.model)
        for col, val in filters.items():
            if hasattr(self.model, col):
                query = query.where(getattr(self.model, col) == val)
        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none() is not None
