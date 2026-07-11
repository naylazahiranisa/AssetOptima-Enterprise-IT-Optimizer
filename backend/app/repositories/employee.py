"""Employee repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Employee)

    async def is_duplicate_email(self, email: str, exclude_id: str | None = None) -> bool:
        filters = {"email": email}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.email == email:
                return False
        return await self.exists(**filters)

    async def is_duplicate_employee_id(
        self, employee_id: str, exclude_id: str | None = None
    ) -> bool:
        filters = {"employee_id": employee_id}
        if exclude_id:
            existing = await self.get_by_id(exclude_id)
            if existing and existing.employee_id == employee_id:
                return False
        return await self.exists(**filters)
