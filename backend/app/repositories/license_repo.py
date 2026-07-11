"""License repository."""

from datetime import datetime, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.license_model import License
from app.repositories.base import BaseRepository


class LicenseRepository(BaseRepository[License]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, License)

    async def is_duplicate_license_key(self, key: str, exclude_id: str | None = None) -> bool:
        filters = {"license_key": key}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.license_key == key:
                return False
        return await self.exists(**filters)

    async def get_expiring(self, days: int = 30) -> list[License]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        threshold = now.replace(day=now.day + days) if hasattr(now, 'day') else now
        from datetime import timedelta
        threshold = now + timedelta(days=days)
        result = await self.db.execute(
            select(self.model).where(
                self.model.expiry_date.isnot(None),
                self.model.expiry_date <= threshold,
                self.model.expiry_date >= now,
                self.model.is_deleted == False,
                self.model.status.in_(["active", "pending_renewal"]),
            ).order_by(self.model.expiry_date.asc())
        )
        return list(result.scalars().all())

    async def get_available_seats(self) -> list[License]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.allocated_seats < self.model.max_seats,
                self.model.is_deleted == False,
                self.model.status == "active",
            ).order_by(desc(self.model.max_seats - self.model.allocated_seats))
        )
        return list(result.scalars().all())

    async def get_by_software(self, software_id: str) -> list[License]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.software_id == software_id,
                self.model.is_deleted == False,
            )
        )
        return list(result.scalars().all())

    async def get_total_costs(self) -> tuple[float, float]:
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(self.model.monthly_cost), 0),
                func.coalesce(func.sum(self.model.annual_cost), 0),
            ).where(self.model.is_deleted == False, self.model.status == "active")
        )
        row = result.one()
        return float(row[0]), float(row[1])
