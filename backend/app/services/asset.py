"""Asset service with assignment, return, and transfer business logic."""

import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetStatus, AssetCondition
from app.models.asset_assignment import AssetAssignment, AssignmentStatus
from app.models.asset_history import AssetHistory, AssetAction
from app.models.notification import Notification, NotificationType
from app.repositories.asset import AssetRepository
from app.repositories.asset_assignment import AssetAssignmentRepository
from app.repositories.asset_history import AssetHistoryRepository
from app.repositories.notification import NotificationRepository
from app.repositories.employee import EmployeeRepository
from app.services.audit_log import record_audit
from app.services.base_service import BaseService
from app.schemas.common import PaginationParams

logger = logging.getLogger(__name__)


class AssetService(BaseService[AssetRepository]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssetRepository(db), db, "assets")
        self.assignment_repo = AssetAssignmentRepository(db)
        self.history_repo = AssetHistoryRepository(db)
        self.notification_repo = NotificationRepository(db)
        self.employee_repo = EmployeeRepository(db)
        self.db = db

    async def list_assets(self, pagination: PaginationParams, filters: dict | None = None):
        base_filters = {"is_deleted": False}
        if filters:
            base_filters.update(filters)
        return await self.list(
            pagination,
            filters=base_filters,
            search_columns=["name", "asset_code", "serial_number"],
        )

    async def get_available_assets(self, pagination: PaginationParams):
        return await self.repo.get_available(pagination, search_columns=["name", "asset_code", "serial_number"])

    def _generate_qr_value(self) -> str:
        return f"QR-{uuid.uuid4().hex[:12].upper()}"

    async def create_asset(self, data: dict, user_id: str | None = None):
        if await self.repo.is_duplicate_asset_code(data.get("asset_code", "")):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset code '{data['asset_code']}' already exists",
            )
        if data.get("serial_number") and await self.repo.is_duplicate_serial_number(data["serial_number"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Serial number '{data['serial_number']}' already exists",
            )

        data["qr_value"] = self._generate_qr_value()
        while await self.repo.is_duplicate_qr_value(data["qr_value"]):
            data["qr_value"] = self._generate_qr_value()

        instance = await self.create(data, user_id)

        await self._record_history(instance.id, AssetAction.CREATED, user_id, notes="Asset created")
        return instance

    async def update_asset(self, record_id: str, data: dict, user_id: str | None = None):
        instance = await self.repo.get_by_id(record_id)
        if not instance or instance.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        if "asset_code" in data and data["asset_code"]:
            if await self.repo.is_duplicate_asset_code(data["asset_code"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Asset code '{data['asset_code']}' already exists",
                )
        if data.get("serial_number"):
            if await self.repo.is_duplicate_serial_number(data["serial_number"], exclude_id=record_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Serial number '{data['serial_number']}' already exists",
                )

        old_condition = instance.condition
        old_status = instance.status

        old = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        instance = await self.repo.update(instance, **data)

        await record_audit(
            self.db, "assets", record_id, "UPDATE",
            performed_by=user_id, old_values=old, new_values=data,
        )

        new_condition = instance.condition
        new_status = instance.status

        if old_condition != new_condition:
            await self._record_history(record_id, AssetAction.CONDITION_CHANGED, user_id,
                                       old_values={"condition": old_condition},
                                       new_values={"condition": new_condition})
        if old_status != new_status:
            await self._record_history(record_id, AssetAction.STATUS_CHANGED, user_id,
                                       old_values={"status": old_status},
                                       new_values={"status": new_status})

        logger.info("Updated asset[%s]", record_id)
        return instance

    async def delete_asset(self, record_id: str, user_id: str | None = None):
        instance = await self.repo.get_by_id(record_id)
        if not instance:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        active = await self.assignment_repo.get_active_by_asset(record_id)
        if active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete asset with active assignment. Return it first.",
            )

        await self.delete(record_id, user_id)

    async def assign_asset(self, asset_id: str, employee_id: str, assigned_by: str,
                           expected_return_date: str | None = None, notes: str | None = None):
        asset = await self.repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        if asset.status != AssetStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset is currently '{asset.status}'. Only available assets can be assigned.",
            )

        employee = await self.employee_repo.get_by_id(employee_id)
        if not employee or employee.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

        expected_date = None
        if expected_return_date:
            try:
                expected_date = datetime.fromisoformat(expected_return_date)
            except ValueError:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid date format for expected_return_date")

        assignment = AssetAssignment(
            asset_id=asset_id,
            employee_id=employee_id,
            assigned_by=assigned_by,
            expected_return_date=expected_date,
            notes=notes,
            status=AssignmentStatus.ASSIGNED,
        )
        self.db.add(assignment)
        await self.db.flush()
        await self.db.refresh(assignment)

        asset.status = AssetStatus.ASSIGNED
        asset.current_employee_id = employee_id
        await self.db.flush()

        await self._record_history(asset_id, AssetAction.ASSIGNED, assigned_by,
                                   new_values={"employee_id": employee_id, "assignment_id": assignment.id},
                                   notes=notes)

        await record_audit(self.db, "assets", asset_id, "ASSIGN", performed_by=assigned_by,
                           new_values={"employee_id": employee_id, "assignment_id": assignment.id})

        await self._create_notification(
            user_id=assigned_by,
            employee_id=employee_id,
            title="Asset Assigned",
            message=f"Asset '{asset.name}' ({asset.asset_code}) has been assigned.",
            ntype=NotificationType.ASSET_ASSIGNED,
            reference_id=asset_id,
        )

        logger.info("Asset[%s] assigned to employee[%s]", asset_id, employee_id)
        return assignment

    async def return_asset(self, asset_id: str, user_id: str, notes: str | None = None, condition: str | None = None):
        asset = await self.repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        if asset.status != AssetStatus.ASSIGNED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset is currently '{asset.status}'. Only assigned assets can be returned.",
            )

        active_assignment = await self.assignment_repo.get_active_by_asset(asset_id)
        if not active_assignment:
            raise HTTPException(status.HTTP_409_CONFLICT, "No active assignment found for this asset.")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        active_assignment.status = AssignmentStatus.RETURNED
        active_assignment.returned_at = now
        if notes:
            active_assignment.notes = notes
        await self.db.flush()

        asset.status = AssetStatus.AVAILABLE
        asset.current_employee_id = None
        if condition:
            asset.condition = condition
        await self.db.flush()

        await self._record_history(asset_id, AssetAction.RETURNED, user_id,
                                   new_values={"assignment_id": active_assignment.id},
                                   notes=notes)

        await record_audit(self.db, "assets", asset_id, "RETURN", performed_by=user_id,
                           new_values={"assignment_id": active_assignment.id})

        await self._create_notification(
            user_id=user_id,
            employee_id=active_assignment.employee_id,
            title="Asset Returned",
            message=f"Asset '{asset.name}' ({asset.asset_code}) has been returned.",
            ntype=NotificationType.ASSET_RETURNED,
            reference_id=asset_id,
        )

        logger.info("Asset[%s] returned", asset_id)
        return active_assignment

    async def transfer_asset(self, asset_id: str, new_employee_id: str, user_id: str, notes: str | None = None):
        asset = await self.repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        if asset.status != AssetStatus.ASSIGNED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset is currently '{asset.status}'. Only assigned assets can be transferred.",
            )

        new_employee = await self.employee_repo.get_by_id(new_employee_id)
        if not new_employee or new_employee.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Target employee not found")

        active_assignment = await self.assignment_repo.get_active_by_asset(asset_id)
        if not active_assignment:
            raise HTTPException(status.HTTP_409_CONFLICT, "No active assignment found for this asset.")

        old_employee_id = active_assignment.employee_id

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        active_assignment.status = AssignmentStatus.TRANSFERRED
        active_assignment.returned_at = now
        await self.db.flush()

        new_assignment = AssetAssignment(
            asset_id=asset_id,
            employee_id=new_employee_id,
            assigned_by=user_id,
            notes=notes,
            status=AssignmentStatus.ASSIGNED,
        )
        self.db.add(new_assignment)
        await self.db.flush()
        await self.db.refresh(new_assignment)

        asset.current_employee_id = new_employee_id
        await self.db.flush()

        await self._record_history(asset_id, AssetAction.TRANSFERRED, user_id,
                                   new_values={
                                       "from_employee_id": old_employee_id,
                                       "to_employee_id": new_employee_id,
                                       "new_assignment_id": new_assignment.id,
                                   },
                                   notes=notes)

        await record_audit(self.db, "assets", asset_id, "TRANSFER", performed_by=user_id,
                           new_values={
                               "from_employee_id": old_employee_id,
                               "to_employee_id": new_employee_id,
                           })

        await self._create_notification(
            user_id=user_id,
            employee_id=new_employee_id,
            title="Asset Transferred",
            message=f"Asset '{asset.name}' ({asset.asset_code}) has been transferred.",
            ntype=NotificationType.ASSET_TRANSFERRED,
            reference_id=asset_id,
        )

        logger.info("Asset[%s] transferred from employee[%s] to employee[%s]",
                     asset_id, old_employee_id, new_employee_id)
        return new_assignment

    async def get_asset_history(self, asset_id: str) -> list[AssetHistory]:
        asset = await self.repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

        return await self.history_repo.get_by_asset(asset_id)

    async def get_asset_qr(self, asset_id: str) -> Asset:
        asset = await self.repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
        return asset

    async def _record_history(self, asset_id: str, action: str, performed_by: str | None,
                              old_values: dict | None = None, new_values: dict | None = None,
                              notes: str | None = None):
        history = AssetHistory(
            asset_id=asset_id,
            action=action,
            performed_by=performed_by,
            performed_at=datetime.now(timezone.utc).replace(tzinfo=None),
            old_values=json.dumps(jsonable_encoder(old_values)) if old_values else None,
            new_values=json.dumps(jsonable_encoder(new_values)) if new_values else None,
            notes=notes,
        )
        self.db.add(history)
        await self.db.flush()

    async def _create_notification(self, user_id: str | None, employee_id: str | None,
                                    title: str, message: str, ntype: str,
                                    reference_id: str | None = None):
        notification = Notification(
            user_id=user_id,
            employee_id=employee_id,
            title=title,
            message=message,
            category=ntype,
            reference_id=reference_id,
        )
        self.db.add(notification)
        await self.db.flush()
