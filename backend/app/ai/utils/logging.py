"""AI-specific logging utilities.

Records prompt, response time, retrieved documents, errors, and model
metadata for observability and audit.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("ai")


def log_ai_request(
    endpoint: str,
    user_id: str | None,
    prompt: str | None,
    response: dict | None,
    processing_time: float,
    model: str = "unknown",
    documents_retrieved: list[str] | None = None,
    error: str | None = None,
) -> None:
    """Structured AI request/response logging."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "user_id": user_id,
        "model": model,
        "prompt_length": len(prompt) if prompt else 0,
        "processing_time_ms": round(processing_time * 1000, 2),
        "documents_retrieved": len(documents_retrieved) if documents_retrieved else 0,
        "error": error,
    }
    if error:
        logger.error("AI request failed: %s", json.dumps(record))
    else:
        logger.info("AI request completed: %s", json.dumps(record))
