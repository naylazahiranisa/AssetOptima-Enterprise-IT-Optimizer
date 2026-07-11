"""ARIMA prediction model (placeholder for future integration)."""

import logging
from typing import Any

from app.ai.base import BasePredictor

logger = logging.getLogger(__name__)


class ARIMAPredictor(BasePredictor):
    """Placeholder for ARIMA time-series forecasting."""

    async def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        logger.debug("ARIMAPredictor.predict not yet implemented")
        return {
            "recommended_count": features.get("current_count", 0),
            "recommended_date": None,
            "confidence": 0.0,
            "summary": "ARIMA model not yet trained. Returning current values as baseline.",
        }

    async def train(self, historical_data: list[dict]) -> None:
        logger.debug("ARIMAPredictor.train not yet implemented (%d records)", len(historical_data))
