from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.asset import Asset
from app.models.employee import Employee
from app.models.notification import Notification, NotificationStatus
from app.schemas.common import build_response
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Retrieve asset counts grouped by status in a single query
    stmt = (
        select(Asset.status, func.count(Asset.id))
        .where(Asset.is_deleted == False)
        .group_by(Asset.status)
    )
    result = await db.execute(stmt)
    status_counts = {status: count for status, count in result.all()}

    assigned_assets = status_counts.get("assigned", 0)
    available_assets = status_counts.get("available", 0)
    maintenance_assets = status_counts.get("maintenance", 0)
    retired_assets = status_counts.get("retired", 0)
    lost_assets = status_counts.get("lost", 0)
    total_assets = sum(status_counts.values())

    total_employees = await db.scalar(select(func.count(Employee.id)))

    unread_notifications = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.status == NotificationStatus.UNREAD,
        )
    )

    return build_response(
        data={
            "total_assets": total_assets,
            "assigned_assets": assigned_assets,
            "available_assets": available_assets,
            "maintenance_assets": maintenance_assets,
            "retired_assets": retired_assets,
            "lost_assets": lost_assets,
            "pending_verifications": 0,
            "total_employees": total_employees or 0,
            "unread_notifications": unread_notifications or 0,
        },
        message="Dashboard stats retrieved successfully",
    )
