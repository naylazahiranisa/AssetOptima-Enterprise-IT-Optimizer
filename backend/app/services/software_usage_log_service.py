"""SoftwareUsageLog service with analytics queries."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.employee import EmployeeRepository
from app.repositories.software import SoftwareRepository
from app.repositories.software_usage_log import SoftwareUsageLogRepository
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class SoftwareUsageLogService(BaseService[SoftwareUsageLogRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(SoftwareUsageLogRepository(db), db, "software_usage_logs")
        self.employee_repo = EmployeeRepository(db)
        self.software_repo = SoftwareRepository(db)
        self.db = db

    async def list_logs(self, pagination: PaginationParams, filters: dict | None = None):
        return await self.list(pagination, filters=filters, search_columns=["ip_address", "os", "device_name"])

    async def create_log(self, data: dict, user_id: str | None = None):
        emp = await self.employee_repo.get_by_id(data.get("employee_id", ""))
        if not emp or emp.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
        sw = await self.software_repo.get_by_id(data.get("software_id", ""))
        if not sw or sw.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")
        if data.get("login_time"):
            try:
                data["login_time"] = datetime.fromisoformat(data["login_time"])
            except ValueError:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid login_time format")
        if data.get("logout_time"):
            try:
                data["logout_time"] = datetime.fromisoformat(data["logout_time"])
            except ValueError:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid logout_time format")
        return await self.create(data, user_id)

    async def update_log(self, record_id: str, data: dict, user_id: str | None = None):
        if data.get("logout_time"):
            try:
                data["logout_time"] = datetime.fromisoformat(data["logout_time"])
            except ValueError:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid logout_time format")
        try:
            return await self.update(record_id, data, user_id)
        except ValueError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Usage log not found")

    async def get_top_software(self, limit: int = 10):
        results = await self.repo.get_top_software(limit)
        output = []
        for sw_id, count, duration in results:
            sw = await self.software_repo.get_by_id(sw_id)
            output.append({
                "software_id": sw_id,
                "software_name": sw.name if sw else "Unknown",
                "usage_count": count,
                "total_duration_seconds": duration,
            })
        return output

    async def get_inactive_employees(self, days: int = 30):
        results = await self.repo.get_inactive_employees(days)
        output = []
        for emp_id, last_login in results:
            emp = await self.employee_repo.get_by_id(emp_id)
            days_inactive = (datetime.now(timezone.utc).replace(tzinfo=None) - last_login).days if last_login else days
            output.append({
                "employee_id": emp_id,
                "employee_name": emp.full_name if emp else "Unknown",
                "days_inactive": days_inactive,
                "last_login": last_login,
            })
        return output

    async def get_usage_by_department(self):
        results = await self.repo.get_usage_by_department()
        dept_data = {}
        for dept_id, count, duration in results:
            dept_data[str(dept_id) if dept_id else "unknown"] = {
                "usage_count": count,
                "total_duration_seconds": duration,
            }
        return dept_data
