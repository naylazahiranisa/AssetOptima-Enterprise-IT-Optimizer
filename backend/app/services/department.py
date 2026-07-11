"""Department service."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.department import DepartmentRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams


class DepartmentService(BaseService[DepartmentRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(DepartmentRepository(db), db, "departments")

    async def list_departments(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            filters={"is_deleted": False},
            search_columns=["name", "code", "description"],
        )

    async def create_department(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_code(data.get("code", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Department code '{data['code']}' already exists",
            )
        return await self.create(data, user_id)

    async def update_department(self, record_id: str, data: dict, user_id: str | None = None):
        if "code" in data and data["code"]:
            if await self.repo.is_duplicate_code(data["code"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Department code '{data['code']}' already exists",
                )
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found")

    async def delete_department(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found")
