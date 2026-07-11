"""Vendor service."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.vendor import VendorRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams


class VendorService(BaseService[VendorRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(VendorRepository(db), db, "vendors")

    async def list_vendors(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            filters={"is_deleted": False},
            search_columns=["name", "code", "contact_person", "email"],
        )

    async def create_vendor(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_code(data.get("code", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vendor code '{data['code']}' already exists",
            )
        return await self.create(data, user_id)

    async def update_vendor(self, record_id: str, data: dict, user_id: str | None = None):
        if "code" in data and data["code"]:
            if await self.repo.is_duplicate_code(data["code"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Vendor code '{data['code']}' already exists",
                )
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vendor not found")

    async def delete_vendor(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Vendor not found")
