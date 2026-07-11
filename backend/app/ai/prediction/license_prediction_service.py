"""License renewal prediction service.

Combines multiple predictors (Prophet, ARIMA, Random Forest) with an
ensemble strategy to recommend license counts and renewal dates.

Now queries real historical data from the database when available.
"""

import logging
import time
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import BasePredictor
from app.ai.utils.logging import log_ai_request
from app.models.software import Software
from app.models.license_model import License
from app.models.employee_software import EmployeeSoftware
from app.models.software_usage_log import SoftwareUsageLog

logger = logging.getLogger(__name__)


class LicensePredictionService:
    """Predicts optimal license counts and renewal timelines."""

    def __init__(
        self,
        db: AsyncSession | None = None,
        predictors: list[BasePredictor] | None = None,
    ):
        self.db = db
        self.predictors = predictors or []

    def register_predictor(self, predictor: BasePredictor) -> None:
        self.predictors.append(predictor)

    async def predict_licenses(
        self,
        features: dict[str, Any],
        user_id: str | None = None,
    ) -> dict[str, Any]:
        start = time.time()
        software_id = features.get("software_id")

        # If DB is available and no detailed features provided, query real data
        if self.db is not None and not features.get("historical_usage"):
            return await self._predict_from_db(software_id, features, user_id, start)

        # Fall back to ensemble predictor logic
        return await self._predict_from_features(features, user_id, start)

    async def _predict_from_db(
        self,
        software_id: str | None,
        features: dict,
        user_id: str | None,
        start: float,
    ) -> dict[str, Any]:
        """Query DB for historical usage and compute predictions."""
        results = []
        total_licensed = 0
        total_allocated = 0
        total_cost = 0.0
        software_names = []

        # Get all active software with licenses
        query = (
            select(
                Software.id,
                Software.name,
                func.sum(License.max_seats).label("total_seats"),
                func.sum(License.allocated_seats).label("allocated_seats"),
                func.sum(License.monthly_cost).label("total_monthly"),
            )
            .join(License, Software.id == License.software_id)
            .where(
                License.status == "active",
                License.is_deleted == False,
                Software.is_deleted == False,
            )
        )
        if software_id:
            query = query.where(Software.id == software_id)

        query = query.group_by(Software.id, Software.name)
        db_results = await self.db.execute(query)

        for row in db_results:
            total_licensed += row.total_seats or 0
            total_allocated += row.allocated_seats or 0
            total_cost += float(row.total_monthly or 0)
            software_names.append(row.name)

            # Count active users for this software
            user_count = await self.db.execute(
                select(func.count(EmployeeSoftware.id))
                .where(
                    EmployeeSoftware.software_id == row.id,
                    EmployeeSoftware.status == "active",
                )
            )
            active_users = user_count.scalar() or 0
            utilization = (active_users / row.total_seats * 100) if row.total_seats else 0

            results.append({
                "software_name": row.name,
                "total_seats": row.total_seats or 0,
                "allocated_seats": row.allocated_seats or 0,
                "active_users": active_users,
                "utilization_percent": round(utilization, 1),
                "monthly_cost": float(row.total_monthly or 0),
            })

        # Simple prediction: if utilization > 80%, recommend +20%; if < 50%, recommend -10%
        predicted_count = total_licensed
        recommendation_reason = "Current count adequate"
        if total_allocated > 0 and total_licensed > 0:
            utilization_rate = total_allocated / total_licensed
            if utilization_rate > 0.8:
                predicted_count = int(total_licensed * 1.2)
                recommendation_reason = f"High utilization ({utilization_rate:.0%}) — consider increasing by 20%"
            elif utilization_rate < 0.5:
                predicted_count = max(1, int(total_licensed * 0.9))
                recommendation_reason = f"Low utilization ({utilization_rate:.0%}) — consider reducing by 10%"

        elapsed = round(time.time() - start, 4)
        log_ai_request("/ai/predict/licenses", user_id, None, None, elapsed)

        return {
            "recommended_count": predicted_count,
            "current_count": total_licensed,
            "allocated_count": total_allocated,
            "total_monthly_cost": round(total_cost, 2),
            "total_annual_cost": round(total_cost * 12, 2),
            "recommendation": recommendation_reason,
            "software_analysed": results,
            "software_names": software_names,
            "confidence": round(min(0.9, 0.5 + 0.05 * len(results)), 4),
            "model_details": results,
            "summary": f"Analysed {len(results)} software product(s). "
                       f"Recommended count: {predicted_count} (current: {total_licensed}).",
            "processing_time": elapsed,
        }

    async def _predict_from_features(
        self,
        features: dict,
        user_id: str | None,
        start: float,
    ) -> dict[str, Any]:
        """Use registered ML predictors (existing logic)."""
        if not self.predictors:
            elapsed = round(time.time() - start, 4)
            log_ai_request("/ai/predict/licenses", user_id, None, None, elapsed)
            return {
                "recommended_count": features.get("current_license_count", 0),
                "recommended_date": features.get("current_renewal_date"),
                "confidence": 0.0,
                "summary": "No prediction models registered. Returning current values.",
                "model_details": [],
            }

        results = []
        for predictor in self.predictors:
            try:
                result = await predictor.predict(features)
                results.append(result)
            except Exception as exc:
                logger.warning("Predictor %s failed: %s", type(predictor).__name__, exc)

        if not results:
            elapsed = round(time.time() - start, 4)
            return {
                "recommended_count": features.get("current_license_count", 0),
                "recommended_date": None,
                "confidence": 0.0,
                "summary": "All prediction models failed. Returning current values.",
                "model_details": [],
            }

        counts = [
            r.get("recommended_count", 0)
            for r in results
            if r.get("recommended_count")
        ]
        confidences = [
            r.get("confidence", 0)
            for r in results
            if r.get("confidence") is not None
        ]

        avg_count = (
            round(sum(counts) / len(counts))
            if counts
            else features.get("current_license_count", 0)
        )
        avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

        elapsed = round(time.time() - start, 4)
        log_ai_request("/ai/predict/licenses", user_id, None, None, elapsed)

        return {
            "recommended_count": max(1, avg_count),
            "recommended_date": results[0].get("recommended_date") if results else None,
            "confidence": avg_confidence,
            "summary": f"Ensemble prediction across {len(results)} model(s). "
                       f"Recommended count: {max(1, avg_count)}.",
            "model_details": results,
            "processing_time": elapsed,
        }
