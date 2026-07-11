"""Shared Pydantic schemas: pagination, standard API envelope, and query params."""

from datetime import datetime, timezone
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class PaginationMeta(BaseModel):
    """Pagination metadata embedded in every list response."""

    page: int
    per_page: int
    total: int
    total_pages: int


class PaginationParams(BaseModel):
    """Query parameters accepted by paginated endpoints."""

    page: int = 1
    per_page: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"
    keyword: str | None = None


class APIRes(BaseModel):
    """Standard API envelope returned by every endpoint."""

    success: bool = True
    message: str = "Operation successful"
    data: Any = None
    pagination: PaginationMeta | None = None
    timestamp: str = ""


def build_response(
    data: Any = None,
    message: str = "Operation successful",
    pagination: PaginationMeta | None = None,
) -> APIRes:
    """Helper to construct a standard API response with an auto-generated timestamp."""
    return APIRes(
        success=True,
        message=message,
        data=jsonable_encoder(data),
        pagination=pagination,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
