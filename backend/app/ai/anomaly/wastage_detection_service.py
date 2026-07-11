"""Software wastage / dormant account detection service.

Analyses usage logs from the database to identify unused licenses,
dormant accounts, and potential cost savings.
"""

import logging
import time
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.utils.logging import log_ai_request
from app.models.employee_software import EmployeeSoftware
from app.models.software import Software
from app.models.license_model import License
from app.models.software_usage_log import SoftwareUsageLog

logger = logging.getLogger(__name__)


class WastageDetectionService:
    """Detect software license wastage from usage patterns using DB data."""

    def __init__(self, db: AsyncSession | None = None, detectors: list | None = None):
        self.db = db
        self.detectors = detectors or []

    def register_detector(self, detector) -> None:
        self.detectors.append(detector)

    async def detect_wastage(
        self,
        usage_data: list[dict] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        start = time.time()

        if self.db is not None and (not usage_data):
            # Query real data from database
            return await self._detect_from_db(user_id, start)
        else:
            # Use provided usage data (existing logic)
            return self._detect_from_data(usage_data or [], start, user_id)

    async def _detect_from_db(
        self, user_id: str | None, start: float
    ) -> dict[str, Any]:
        """Query DB for dormant licenses and unused accounts."""
        dormant = []
        total_analysed = 0
        total_potential_savings = 0.0

        # Find all active employee-software assignments
        assignments_query = await self.db.execute(
            select(
                EmployeeSoftware.employee_id,
                EmployeeSoftware.software_id,
                EmployeeSoftware.assigned_at,
                Software.name.label("software_name"),
                License.monthly_cost,
                License.annual_cost,
            )
            .join(Software, EmployeeSoftware.software_id == Software.id)
            .join(License, EmployeeSoftware.license_id == License.id)
            .where(
                EmployeeSoftware.status == "active",
                Software.is_deleted == False,
            )
        )
        assignments = assignments_query.all()

        for row in assignments:
            total_analysed += 1
            employee_id = row.employee_id
            software_id = row.software_id

            # Check latest usage log
            log_query = await self.db.execute(
                select(func.max(SoftwareUsageLog.login_time))
                .where(
                    SoftwareUsageLog.employee_id == employee_id,
                    SoftwareUsageLog.software_id == software_id,
                )
            )
            last_login = log_query.scalar()

            inactive_days = 0
            if last_login is not None:
                inactive_days = (time.time() - last_login.timestamp()) / 86400
            else:
                # Never used — check how long since assigned
                if row.assigned_at:
                    inactive_days = (time.time() - row.assigned_at.timestamp()) / 86400
                else:
                    inactive_days = 365  # Assume very old

            if inactive_days >= 30:
                monthly_cost = float(row.monthly_cost or 0)
                annual_cost = float(row.annual_cost or 0) or (monthly_cost * 12)
                savings = annual_cost
                total_potential_savings += savings

                dormant.append({
                    "employee_id": employee_id,
                    "software_id": software_id,
                    "software_name": row.software_name or "Unknown",
                    "inactive_days": round(inactive_days),
                    "last_login": last_login.isoformat() if last_login else None,
                    "monthly_cost": monthly_cost,
                    "annual_cost": annual_cost,
                    "potential_savings": round(savings, 2),
                    "status": "never_used" if last_login is None else "dormant",
                })

        elapsed = round(time.time() - start, 4)
        log_ai_request("/ai/anomaly/licenses", user_id, None, None, elapsed)

        return {
            "dormant_accounts": dormant,
            "dormant_count": len(dormant),
            "total_analysed": total_analysed,
            "potential_annual_savings": round(total_potential_savings, 2),
            "confidence": 0.85 if dormant else 1.0,
            "detection_method": "database_query",
            "processing_time": elapsed,
        }

    def _detect_from_data(
        self, usage_data: list[dict], start: float, user_id: str | None
    ) -> dict[str, Any]:
        """Analyze provided usage data (original logic)."""
        dormant = []
        for record in usage_data:
            inactive_days = record.get("inactive_days", 0) or 0
            if inactive_days >= 30:
                dormant.append({
                    "employee_id": record.get("employee_id"),
                    "software_id": record.get("software_id"),
                    "software_name": record.get("software_name", "Unknown"),
                    "inactive_days": inactive_days,
                    "last_login": record.get("last_login"),
                    "status": "dormant",
                })

        total_potential_savings = 0.0
        for d in dormant:
            monthly_cost = next(
                (
                    r.get("monthly_cost", 0)
                    for r in usage_data
                    if r.get("software_id") == d["software_id"]
                ),
                0.0,
            )
            d["potential_savings"] = round(monthly_cost * 12, 2)
            total_potential_savings += d["potential_savings"]

        elapsed = round(time.time() - start, 4)
        log_ai_request("/ai/anomaly/licenses", user_id, None, None, elapsed)

        return {
            "dormant_accounts": dormant,
            "dormant_count": len(dormant),
            "total_analysed": len(usage_data),
            "potential_annual_savings": round(total_potential_savings, 2),
            "confidence": 0.85 if dormant else 1.0,
            "detection_method": "provided_data",
            "processing_time": elapsed,
        }
