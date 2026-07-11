"""Main AI orchestration service.

Wires together all AI sub-modules (RAG assistant, prediction, wastage
detection, recommendation, analytics) into a single injectable service.
"""

import logging
import time
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.anomaly.wastage_detection_service import WastageDetectionService
from app.ai.assistant.assistant_service import AssistantService
from app.ai.prediction.license_prediction_service import LicensePredictionService
from app.ai.recommendation.engine import RecommendationEngine
from app.ai.utils.response_formatter import format_response
from app.models.software import Software
from app.models.license_model import License
from app.models.employee_software import EmployeeSoftware
from app.models.asset import Asset

logger = logging.getLogger(__name__)


class AIService:
    """Top-level AI service that delegates to specialised sub-services."""

    def __init__(
        self,
        assistant: AssistantService | None = None,
        predictor: LicensePredictionService | None = None,
        wastage: WastageDetectionService | None = None,
        recommender: RecommendationEngine | None = None,
    ):
        self.assistant = assistant
        self.predictor = predictor
        self.wastage = wastage
        self.recommender = recommender

    async def chat(
        self,
        question: str,
        user_id: str | None = None,
        top_k: int = 5,
        domain: str | None = None,
    ) -> dict:
        if not self.assistant:
            return format_response(
                message="AI assistant not configured", data=None, confidence=0.0
            )
        result = await self.assistant.chat(question, user_id, top_k, domain)
        sources = result.get("source_documents", [])
        return format_response(
            data={
                "answer": result.get("answer", ""),
                "source_documents": sources,
            },
            confidence=result.get("confidence", 0.0),
            source_documents=sources,
            processing_time=result.get("processing_time", 0.0),
        )

    async def predict_licenses(
        self, features: dict, user_id: str | None = None
    ) -> dict:
        if not self.predictor:
            return format_response(
                message="Prediction service not configured",
                data=None,
                confidence=0.0,
            )
        result = await self.predictor.predict_licenses(features, user_id)
        return format_response(
            data=result,
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
        )

    async def detect_anomalies(
        self,
        usage_data: list[dict],
        user_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> dict:
        if not self.wastage:
            return format_response(
                message="Anomaly detection not configured",
                data=None,
                confidence=0.0,
            )
        result = await self.wastage.detect_wastage(
            usage_data=usage_data, user_id=user_id
        )
        return format_response(
            data=result,
            confidence=result.get("confidence", 0.0),
            processing_time=result.get("processing_time", 0.0),
        )

    async def get_recommendations(
        self, context: dict, user_id: str | None = None
    ) -> dict:
        if not self.recommender:
            return format_response(
                message="Recommendation engine not configured", data=None
            )
        result = await self.recommender.generate(context, user_id)
        return format_response(
            data=result,
            processing_time=result.get("processing_time", 0.0),
        )

    async def get_analytics(self, db: AsyncSession | None = None) -> dict:
        start = time.time()

        if db is None:
            data = {
                "most_expensive_software": [],
                "unused_assets": [],
                "license_utilization": {
                    "total": 0,
                    "used": 0,
                    "utilization_rate": 0.0,
                },
                "department_cost": {},
                "risk_level": "low",
            }
            elapsed = round(time.time() - start, 4)
            return format_response(data=data, processing_time=elapsed)

        # Real analytics from database
        try:
            # Most expensive software by monthly cost
            sw_query = await db.execute(
                select(
                    Software.name,
                    func.sum(License.monthly_cost).label("total_monthly"),
                    func.sum(License.annual_cost).label("total_annual"),
                )
                .join(License, Software.id == License.software_id)
                .where(
                    License.status == "active",
                    License.is_deleted == False,
                    Software.is_deleted == False,
                )
                .group_by(Software.name)
                .order_by(func.sum(License.monthly_cost).desc())
                .limit(10)
            )
            expensive_sw = [
                {
                    "name": row.name,
                    "monthly_cost": float(row.total_monthly or 0),
                    "annual_cost": float(row.total_annual or 0),
                }
                for row in sw_query
            ]

            # License utilization
            lic_query = await db.execute(
                select(
                    func.sum(License.max_seats).label("total"),
                    func.sum(License.allocated_seats).label("allocated"),
                ).where(License.is_deleted == False)
            )
            lic_row = lic_query.one()
            total_seats = lic_row.total or 0
            allocated = lic_row.allocated or 0
            utilization = (
                round((allocated / total_seats) * 100, 1) if total_seats > 0 else 0.0
            )

            # Active users count
            user_count = await db.execute(
                select(func.count(EmployeeSoftware.id)).where(
                    EmployeeSoftware.status == "active"
                )
            )
            active_users = user_count.scalar() or 0

            # Unused assets
            asset_query = await db.execute(
                select(func.count(Asset.id)).where(
                    Asset.status == "available", Asset.is_deleted == False
                )
            )
            unused_assets = asset_query.scalar() or 0

            data = {
                "most_expensive_software": expensive_sw,
                "license_utilization": {
                    "total": total_seats,
                    "used": allocated,
                    "active_users": active_users,
                    "utilization_rate": utilization,
                },
                "unused_assets_count": unused_assets,
                "total_software": len(expensive_sw),
                "risk_level": "low" if utilization > 50 else "medium",
            }
        except Exception as exc:
            logger.error("Analytics DB query failed: %s", exc)
            data = {
                "error": str(exc),
                "most_expensive_software": [],
                "license_utilization": {},
                "unused_assets_count": 0,
            }

        elapsed = round(time.time() - start, 4)
        return format_response(data=data, processing_time=elapsed)
