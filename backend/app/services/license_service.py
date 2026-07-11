"""License service with seat allocation logic."""

import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.license_model import LicenseStatus
from app.repositories.license_repo import LicenseRepository
from app.repositories.software import SoftwareRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class LicenseService(BaseService[LicenseRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(LicenseRepository(db), db, "licenses")
        self.software_repo = SoftwareRepository(db)
        self.db = db

    async def list_licenses(self, pagination: PaginationParams, filters: dict | None = None):
        base = {"is_deleted": False}
        if filters:
            base.update(filters)
        return await self.list(pagination, filters=base, search_columns=["license_key"])

    async def create_license(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_license_key(data.get("license_key", "")):
            raise HTTPException(status.HTTP_409_CONFLICT, f"License key '{data['license_key']}' already exists")

        sw = await self.software_repo.get_by_id(data.get("software_id", ""))
        if not sw or sw.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")

        for date_field in ["purchase_date", "renewal_date", "expiry_date"]:
            if data.get(date_field):
                try:
                    datetime.fromisoformat(data[date_field])
                except ValueError:
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid {date_field} format")

        return await self.create(data, user_id)

    async def update_license(self, record_id: str, data: dict, user_id: str | None = None):
        if "license_key" in data and data["license_key"]:
            if await self.repo.is_duplicate_license_key(data["license_key"], exclude_id=record_id):
                raise HTTPException(status.HTTP_409_CONFLICT, f"License key '{data['license_key']}' already exists")

        for date_field in ["purchase_date", "renewal_date", "expiry_date"]:
            if data.get(date_field):
                try:
                    datetime.fromisoformat(data[date_field])
                except ValueError:
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Invalid {date_field} format")

        if "max_seats" in data and data["max_seats"] is not None:
            instance = await self.repo.get_by_id(record_id)
            if instance and data["max_seats"] < instance.allocated_seats:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Cannot reduce max_seats below current allocation ({instance.allocated_seats})",
                )

        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")

    async def delete_license(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")

    async def get_expiring(self, days: int = 30):
        return await self.repo.get_expiring(days)

    async def get_available_seats(self):
        return await self.repo.get_available_seats()

    async def get_unused_licenses(self):
        all_licenses = await self.repo.get_all(
            PaginationParams(page=1, per_page=9999),
            filters={"is_deleted": False, "status": "active"},
        )
        items, _ = all_licenses
        return [lic for lic in items if lic.allocated_seats == 0]

    async def get_cost_summary(self):
        total_monthly, total_annual = await self.repo.get_total_costs()
        return {
            "total_monthly_cost": total_monthly,
            "total_annual_cost": total_annual,
        }

    async def increment_allocated(self, license_id: str) -> None:
        lic = await self.repo.get_by_id(license_id)
        if not lic:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")
        if lic.allocated_seats >= lic.max_seats:
            raise HTTPException(status.HTTP_409_CONFLICT, "No available seats on this license")
        lic.allocated_seats += 1
        await self.db.flush()

    async def decrement_allocated(self, license_id: str) -> None:
        lic = await self.repo.get_by_id(license_id)
        if not lic:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")
        if lic.allocated_seats > 0:
            lic.allocated_seats -= 1
            await self.db.flush()
