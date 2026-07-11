"""AssetOptima — Enterprise IT Asset & License Optimizer.

FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import v1_router
from app.config.settings import settings
from app.core.logging import configure_logging
from app.database.init_db import test_connection
from app.database.session import AsyncSessionLocal
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan: startup / shutdown lifecycle."""
    configure_logging()
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Create all tables on startup (dev mode with SQLite)
    from app.database.base import Base
    from app.database.connection import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    connected = await test_connection()
    if connected:
        # Seed default super admin on first run
        from app.auth.service import seed_super_admin

        async with AsyncSessionLocal() as session:
            await seed_super_admin(session)
    else:
        logger.warning("Application started without database connectivity")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

# ------------------------------------------------------------------ #
# Middleware — order matters (last added = outer layer)
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# ------------------------------------------------------------------ #
# Global exception handlers — consistent JSON errors
# ------------------------------------------------------------------ #
register_exception_handlers(app)

# ------------------------------------------------------------------ #
# Routers
# ------------------------------------------------------------------ #
app.include_router(v1_router)


@app.get("/")
async def root():
    """Root endpoint — returns project metadata and status."""
    return {
        "project": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health_check():
    """Liveness probe for container orchestration and monitoring."""
    return {"status": "healthy"}
