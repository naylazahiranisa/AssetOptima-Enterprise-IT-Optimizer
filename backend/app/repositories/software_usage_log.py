"""SoftwareUsageLog repository."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.software_usage_log import SoftwareUsageLog
from app.repositories.base import BaseRepository


class SoftwareUsageLogRepository(BaseRepository[SoftwareUsageLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SoftwareUsageLog)

    async def get_top_software(self, limit: int = 10) -> list[tuple[str, int, int]]:
        result = await self.db.execute(
            select(
                self.model.software_id,
                func.count(self.model.id).label("usage_count"),
                func.coalesce(func.sum(self.model.session_duration_seconds), 0).label("total_duration"),
            ).group_by(self.model.software_id).order_by(desc("usage_count")).limit(limit)
        )
        return list(result.all())

    async def get_inactive_employees(self, days: int = 30) -> list[tuple[str, datetime | None]]:
        threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        subq = select(
            self.model.employee_id,
            func.max(self.model.login_time).label("last_login"),
        ).group_by(self.model.employee_id).subquery()

        result = await self.db.execute(
            select(subq.c.employee_id, subq.c.last_login).where(
                subq.c.last_login < threshold
            ).order_by(subq.c.last_login.asc())
        )
        return list(result.all())

    async def get_usage_by_department(self) -> list[tuple[str | None, int, float]]:
        result = await self.db.execute(
            select(
                self.model.department_id,
                func.count(self.model.id),
                func.coalesce(func.sum(self.model.session_duration_seconds), 0),
            ).group_by(self.model.department_id)
        )
        return list(result.all())
