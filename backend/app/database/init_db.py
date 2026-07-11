"""Database initialisation and connection verification.

Used during application startup to confirm the database is reachable.
Does **not** create tables — that is the responsibility of Alembic
migrations.
"""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import engine

logger = logging.getLogger(__name__)


async def test_connection() -> bool:
    """Execute a lightweight query to verify database reachability.

    Returns ``True`` on success, ``False`` on any connectivity failure.
    """
    try:
        async with asyncio.timeout(5):
            async with AsyncSession(engine) as session:
                await session.execute(text("SELECT 1"))
        logger.info("Database connection test: PASSED")
        return True
    except (asyncio.TimeoutError, Exception) as exc:
        logger.error("Database connection test: FAILED — %s", exc)
        return False
