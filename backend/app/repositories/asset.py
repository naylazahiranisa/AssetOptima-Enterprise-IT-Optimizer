"""Asset repository."""

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Asset)

    async def is_duplicate_asset_code(self, code: str, exclude_id: str | None = None) -> bool:
        filters = {"asset_code": code}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.asset_code == code:
                return False
        return await self.exists(**filters)

    async def is_duplicate_serial_number(self, serial: str, exclude_id: str | None = None) -> bool:
        filters = {"serial_number": serial}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.serial_number == serial:
                return False
        return await self.exists(**filters)

    async def is_duplicate_qr_value(self, qr: str, exclude_id: str | None = None) -> bool:
        filters = {"qr_value": qr}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.qr_value == qr:
                return False
        return await self.exists(**filters)

    async def get_available(self, pagination, filters: dict | None = None, search_columns: list[str] | None = None):
        base_filters = filters or {}
        base_filters["status"] = "available"
        base_filters["is_deleted"] = False
        return await self.get_all(pagination, base_filters, search_columns)

    async def get_by_employee(self, employee_id: str) -> list[Asset]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.current_employee_id == employee_id,
                self.model.is_deleted == False,
            )
        )
        return list(result.scalars().all())
