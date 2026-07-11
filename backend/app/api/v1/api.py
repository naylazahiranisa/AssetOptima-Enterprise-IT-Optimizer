"""Top-level v1 router aggregator.

Includes all endpoint routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    companies,
    departments,
    employees,
    roles,
    users,
    locations,
    vendors,
    asset_categories,
    assets,
    software_categories,
    software,
    licenses,
    employee_software,
    software_usage_logs,
    notifications,
    notification_preferences,
    audit_logs,
    system_activities,
    dashboard,
)
from app.ai.router import router as ai_router
from app.auth.router import router as auth_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth_router)
v1_router.include_router(companies.router)
v1_router.include_router(departments.router)
v1_router.include_router(employees.router)
v1_router.include_router(roles.router)
v1_router.include_router(users.router)
v1_router.include_router(locations.router)
v1_router.include_router(vendors.router)
v1_router.include_router(asset_categories.router)
v1_router.include_router(assets.router)
v1_router.include_router(software_categories.router)
v1_router.include_router(licenses.router)
v1_router.include_router(software.router)
v1_router.include_router(employee_software.router)
v1_router.include_router(software_usage_logs.router)
v1_router.include_router(notifications.router)
v1_router.include_router(notification_preferences.router)
v1_router.include_router(audit_logs.router)
v1_router.include_router(system_activities.router)
v1_router.include_router(dashboard.router)
v1_router.include_router(ai_router)
