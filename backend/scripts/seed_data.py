#!/usr/bin/env python3
"""Seed the database with initial reference data for development/testing.

Usage:
    python scripts/seed_data.py
"""

import asyncio
import logging

from app.database.session import AsyncSessionLocal
from app.auth.service import seed_super_admin

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
logger = logging.getLogger(__name__)


async def seed():
    async with AsyncSessionLocal() as session:
        await seed_super_admin(session)
        logger.info("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
