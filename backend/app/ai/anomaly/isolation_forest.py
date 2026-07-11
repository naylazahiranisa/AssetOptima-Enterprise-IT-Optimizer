"""Isolation Forest anomaly detector (placeholder for future integration)."""

import logging
from typing import Any

from app.ai.base import BaseAnomalyDetector

logger = logging.getLogger(__name__)


class IsolationForestDetector(BaseAnomalyDetector):
    """Placeholder for scikit-learn Isolation Forest."""

    async def detect(self, features: list[dict]) -> list[dict]:
        logger.debug("IsolationForestDetector.detect not yet implemented")
        return [
            {
                "id": item.get("id", "unknown"),
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "details": "Model not trained. No anomalies detected.",
            }
            for item in features
        ]

    async def fit(self, data: list[dict]) -> None:
        logger.debug("IsolationForestDetector.fit not yet implemented (%d records)", len(data))
