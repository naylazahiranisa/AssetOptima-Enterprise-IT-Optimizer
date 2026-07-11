"""Dependencies module: FastAPI dependency injection for services and utilities."""

from app.dependencies.service_factory import get_asset_service, get_company_service

__all__ = [
    "get_asset_service",
    "get_company_service",
]
