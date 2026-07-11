"""EmployeeSoftware service with assign/remove/transfer logic."""

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee_software import EmployeeSoftware, EmployeeSoftwareStatus
from app.repositories.employee import EmployeeRepository
from app.repositories.employee_software import EmployeeSoftwareRepository
from app.repositories.license_repo import LicenseRepository
from app.repositories.software import SoftwareRepository
from app.services.audit_log import record_audit
from app.services.license_service import LicenseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class EmployeeSoftwareService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EmployeeSoftwareRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.software_repo = SoftwareRepository(db)
        self.license_repo = LicenseRepository(db)
        self.license_service = LicenseService(db)

    async def list_assignments(self, pagination: PaginationParams, filters: dict | None = None):
        return await self.repo.get_all(pagination, filters=filters)

    async def get(self, record_id: str):
        return await self.repo.get_by_id(record_id)

    async def assign_software(self, employee_id: str, software_id: str,
                              license_id: str | None = None, assigned_by: str | None = None,
                              notes: str | None = None):
        emp = await self.employee_repo.get_by_id(employee_id)
        if not emp or emp.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

        sw = await self.software_repo.get_by_id(software_id)
        if not sw or sw.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Software not found")

        existing = await self.repo.get_active_by_employee_and_software(employee_id, software_id)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Employee already has this software assigned")

        lic = None
        if license_id:
            lic = await self.license_repo.get_by_id(license_id)
            if not lic or lic.is_deleted:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")
            if lic.allocated_seats >= lic.max_seats:
                raise HTTPException(status.HTTP_409_CONFLICT, "No available seats on this license")
            lic.allocated_seats += 1
        else:
            licenses = await self.license_repo.get_by_software(software_id)
            active_lics = [l for l in licenses if l.status == "active" and l.allocated_seats < l.max_seats]
            if active_lics:
                lic = active_lics[0]
                lic.allocated_seats += 1
                license_id = lic.id
            else:
                raise HTTPException(status.HTTP_409_CONFLICT, "No available seats on any license for this software")

        assignment = EmployeeSoftware(
            employee_id=employee_id,
            software_id=software_id,
            license_id=license_id,
            assigned_by=assigned_by,
            notes=notes,
            status=EmployeeSoftwareStatus.ACTIVE,
        )
        self.db.add(assignment)
        await self.db.flush()
        await self.db.refresh(assignment)

        await record_audit(self.db, "employee_software", assignment.id, "ASSIGN",
                           performed_by=assigned_by,
                           new_values={"employee_id": employee_id, "software_id": software_id, "license_id": license_id})
        logger.info("Software[%s] assigned to employee[%s]", software_id, employee_id)
        return assignment

    async def remove_software(self, record_id: str, user_id: str | None = None, notes: str | None = None):
        assignment = await self.repo.get_by_id(record_id)
        if not assignment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
        if assignment.status != EmployeeSoftwareStatus.ACTIVE:
            raise HTTPException(status.HTTP_409_CONFLICT, "Assignment is not active")

        old_status = assignment.status
        assignment.status = EmployeeSoftwareStatus.REMOVED
        if notes:
            assignment.notes = notes
        await self.db.flush()

        if assignment.license_id:
            try:
                await self.license_service.decrement_allocated(assignment.license_id)
            except HTTPException:
                pass

        await record_audit(self.db, "employee_software", record_id, "REMOVE",
                           performed_by=user_id,
                           old_values={"status": old_status},
                           new_values={"status": EmployeeSoftwareStatus.REMOVED, "license_id": assignment.license_id})
        logger.info("Software removed from employee[%s]", assignment.employee_id)
        return assignment

    async def transfer_software(self, from_employee_id: str, to_employee_id: str,
                                software_id: str, user_id: str | None = None,
                                notes: str | None = None):
        if from_employee_id == to_employee_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Cannot transfer to the same employee")

        to_emp = await self.employee_repo.get_by_id(to_employee_id)
        if not to_emp or to_emp.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Target employee not found")

        existing = await self.repo.get_active_by_employee_and_software(to_employee_id, software_id)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Target employee already has this software")

        current = await self.repo.get_active_by_employee_and_software(from_employee_id, software_id)
        if not current:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No active assignment found for this employee and software")

        old_license_id = current.license_id
        current.status = EmployeeSoftwareStatus.TRANSFERRED
        await self.db.flush()

        new_assignment = EmployeeSoftware(
            employee_id=to_employee_id,
            software_id=software_id,
            license_id=old_license_id,
            assigned_by=user_id,
            notes=notes,
            status=EmployeeSoftwareStatus.ACTIVE,
        )
        self.db.add(new_assignment)
        await self.db.flush()
        await self.db.refresh(new_assignment)

        await record_audit(self.db, "employee_software", new_assignment.id, "TRANSFER",
                           performed_by=user_id,
                           new_values={
                               "from_employee_id": from_employee_id,
                               "to_employee_id": to_employee_id,
                               "software_id": software_id,
                               "license_id": old_license_id,
                           })
        logger.info("Software[%s] transferred from employee[%s] to employee[%s]",
                     software_id, from_employee_id, to_employee_id)
        return new_assignment
