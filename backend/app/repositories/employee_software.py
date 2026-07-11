"""EmployeeSoftware repository."""

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee_software import EmployeeSoftware
from app.repositories.base import BaseRepository


class EmployeeSoftwareRepository(BaseRepository[EmployeeSoftware]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, EmployeeSoftware)

    async def get_active_by_employee(self, employee_id: str) -> list[EmployeeSoftware]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.employee_id == employee_id,
                self.model.status == "active",
            )
        )
        return list(result.scalars().all())

    async def get_active_by_software(self, software_id: str) -> list[EmployeeSoftware]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.software_id == software_id,
                self.model.status == "active",
            )
        )
        return list(result.scalars().all())

    async def get_active_by_employee_and_software(self, employee_id: str, software_id: str) -> EmployeeSoftware | None:
        result = await self.db.execute(
            select(self.model).where(
                self.model.employee_id == employee_id,
                self.model.software_id == software_id,
                self.model.status == "active",
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active_by_license(self, license_id: str) -> list[EmployeeSoftware]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.license_id == license_id,
                self.model.status == "active",
            )
        )
        return list(result.scalars().all())
