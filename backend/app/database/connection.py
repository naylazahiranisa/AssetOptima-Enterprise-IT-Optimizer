"""SQLAlchemy async engine creation.

Reads the effective database URL from application settings and
creates a reusable async engine with connection-pool defaults.
"""

import logging

from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import settings

logger = logging.getLogger(__name__)

_engine_kwargs: dict = {"url": settings.database_url, "echo": False}

if "postgresql" in settings.database_url:
    _engine_kwargs["pool_size"] = settings.POSTGRES_POOL_SIZE
    _engine_kwargs["max_overflow"] = settings.POSTGRES_MAX_OVERFLOW
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(**_engine_kwargs)
