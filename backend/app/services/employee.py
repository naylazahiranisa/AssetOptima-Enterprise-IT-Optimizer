"""Employee service."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.employee import EmployeeRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams


class EmployeeService(BaseService[EmployeeRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeRepository(db), db, "employees")

    async def list_employees(self, pagination: PaginationParams):
        return await self.list(
            pagination,
            filters={"is_deleted": False},
            search_columns=["full_name", "email", "employee_id", "position"],
        )

    async def create_employee(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_email(data.get("email", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{data['email']}' already exists",
            )
        if await self.repo.is_duplicate_employee_id(data.get("employee_id", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee ID '{data['employee_id']}' already exists",
            )
        return await self.create(data, user_id)

    async def update_employee(self, record_id: str, data: dict, user_id: str | None = None):
        if "email" in data and data["email"]:
            if await self.repo.is_duplicate_email(data["email"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{data['email']}' already exists",
                )
        if "employee_id" in data and data["employee_id"]:
            if await self.repo.is_duplicate_employee_id(data["employee_id"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Employee ID '{data['employee_id']}' already exists",
                )
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    async def delete_employee(self, record_id: str, user_id: str | None = None):
        try:
            await self.delete(record_id, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
