"""Health-check endpoints for readiness probes and monitoring."""

from fastapi import APIRouter

from app.database.init_db import test_connection

router = APIRouter()


@router.get("/")
async def root_health():
    """Root endpoint returning project metadata and status."""
    return {
        "project": "AssetOptima",
        "status": "running",
        "version": "1.0.0",
    }


@router.get("/health")
async def liveness_check():
    """Liveness probe — returns healthy when the service is up."""
    return {"status": "healthy"}


@router.get("/health/database")
async def database_health():
    """Database connectivity probe."""
    connected = await test_connection()
    if connected:
        return {"database": "connected"}
    return {"database": "disconnected"}
