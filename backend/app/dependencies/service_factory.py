"""Service factory dependencies for proper DI with FastAPI.

Instead of instantiating services inside endpoints, use these
dependencies for better testability and separation of concerns.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.asset import AssetService
from app.services.company import CompanyService


async def get_asset_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AssetService:
    return AssetService(db)


async def get_company_service(db: Annotated[AsyncSession, Depends(get_db)]) -> CompanyService:
    return CompanyService(db)
