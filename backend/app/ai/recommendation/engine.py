"""Recommendation engine that generates actionable IT asset recommendations.

Combines insights from RAG, prediction, and wastage detection to
produce prioritised recommendations.
"""

import logging
import time
from typing import Any

from app.ai.utils.logging import log_ai_request

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates IT asset management recommendations based on data analysis."""

    async def generate(self, context: dict[str, Any],
                       user_id: str | None = None) -> dict[str, Any]:
        start = time.time()

        recommendations = []

        # License reclamation
        dormant = context.get("dormant_accounts", [])
        if dormant:
            recommendations.append({
                "type": "reclaim_license",
                "priority": "high",
                "title": f"Reclaim {len(dormant)} unused license(s)",
                "description": f"{len(dormant)} license(s) have been inactive for 30+ days. Reclaim to reduce costs.",
                "estimated_savings": context.get("potential_annual_savings", 0),
                "action_url": "/software/licenses",
            })

        # License purchase
        predicted_count = context.get("predicted_count")
        current_count = context.get("current_license_count")
        if predicted_count and current_count and predicted_count > current_count:
            additional = predicted_count - current_count
            recommendations.append({
                "type": "purchase_license",
                "priority": "medium",
                "title": f"Purchase {additional} additional license(s)",
                "description": f"Predicted demand ({predicted_count}) exceeds current count ({current_count}).",
                "estimated_savings": 0,
                "action_url": "/software/licenses",
            })

        # Expiring licenses
        expiring = context.get("expiring_licenses", [])
        if expiring:
            recommendations.append({
                "type": "renew_license",
                "priority": "critical" if any(
                    e.get("days_until_expiry", 999) <= 30 for e in expiring
                ) else "high",
                "title": f"{len(expiring)} license(s) expiring soon",
                "description": "Review and renew expiring licenses to avoid service interruption.",
                "estimated_savings": 0,
                "action_url": "/software/licenses?status=expiring",
            })

        # Asset retirement
        unused_assets = context.get("unused_assets", [])
        if unused_assets:
            recommendations.append({
                "type": "retire_asset",
                "priority": "low",
                "title": f"Retire {len(unused_assets)} unused asset(s)",
                "description": f"{len(unused_assets)} asset(s) show no recent activity. Consider retirement or reassignment.",
                "estimated_savings": sum(a.get("annual_cost", 0) for a in unused_assets),
                "action_url": "/assets?status=unused",
            })

        elapsed = round(time.time() - start, 4)
        log_ai_request("/ai/recommendations", user_id, None, None, elapsed)

        return {
            "recommendations": sorted(recommendations, key=lambda r: ["critical", "high", "medium", "low"].index(r["priority"])),
            "total": len(recommendations),
            "processing_time": elapsed,
        }
