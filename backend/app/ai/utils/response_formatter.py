"""Standard AI response formatter.

All AI endpoints return a uniform response envelope for consistency
across the Web Command Center, Flutter app, and AI Analytics Engine.
"""

import time
from typing import Any

from app.ai.base import AIResponse


def format_response(
    data: Any = None,
    message: str = "Operation successful",
    confidence: float | None = None,
    source_documents: list[dict] | None = None,
    processing_time: float | None = None,
) -> dict:
    """Build a standardised AI response dict."""
    if processing_time is None:
        processing_time = round(time.time() - _get_start_time(), 4)
    resp = AIResponse(
        success=True,
        message=message,
        data=data,
        confidence=confidence,
        source_documents=source_documents or [],
        processing_time=processing_time,
    )
    return {
        "success": resp.success,
        "message": resp.message,
        "data": resp.data,
        "confidence": resp.confidence,
        "source_documents": resp.source_documents,
        "processing_time": resp.processing_time,
        "timestamp": resp.timestamp,
    }


def error_response(message: str = "An error occurred",
                   processing_time: float = 0.0) -> dict:
    """Build a standardised error response."""
    resp = AIResponse(
        success=False,
        message=message,
        processing_time=processing_time,
    )
    return {
        "success": resp.success,
        "message": resp.message,
        "data": None,
        "confidence": None,
        "source_documents": [],
        "processing_time": resp.processing_time,
        "timestamp": resp.timestamp,
    }


# Simple timer context tracking
_start_times: dict[str, float] = {}


def _get_start_time() -> float:
    return _start_times.get("_global", time.time())


def start_timer() -> None:
    _start_times["_global"] = time.time()
