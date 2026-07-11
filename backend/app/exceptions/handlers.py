"""Global exception handlers for consistent JSON error responses.

Registers handlers for common HTTP errors and unexpected exceptions,
ensuring every error response follows the same envelope format.
"""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def _error_response(status_code: int, message: str, details: list | None = None) -> JSONResponse:
    body = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": status_code,
            "details": details or [],
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(body))


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTP %d — %s | %s %s", exc.status_code, exc.detail, request.method, request.url.path)
    return _error_response(status_code=exc.status_code, message=str(exc.detail))


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return _error_response(status_code=exc.status_code, message=str(exc.detail))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    logger.warning("Validation error — %s %s: %s", request.method, request.url.path, errors)
    return _error_response(
        status_code=422,
        message="Request validation failed",
        details=[{"field": e.get("loc", []), "msg": e.get("msg", ""), "type": e.get("type", "")} for e in errors],
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception — %s %s", request.method, request.url.path)
    return _error_response(
        status_code=500,
        message="An internal server error occurred. Please try again later.",
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
