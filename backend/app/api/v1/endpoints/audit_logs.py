"""AuditLog read-only endpoints for compliance and traceability.

Audit logs are immutable — only GET operations are exposed.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", summary="List audit logs")
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "performed_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    action: str | None = Query(None, alias="action"),
    table_name: str | None = Query(None, alias="table_name"),
    performed_by: str | None = Query(None, alias="performed_by"),
):
    filters = {}
    if action:
        filters["action"] = action
    if table_name:
        filters["table_name"] = table_name
    if performed_by:
        filters["performed_by"] = performed_by
    service = AuditLogService(db)
    items, meta = await service.list_audit_logs(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(data=[AuditLogResponse.model_validate(a) for a in items], pagination=meta)


@router.get("/{audit_id}", summary="Get audit log by ID")
async def get_audit_log(
    audit_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    service = AuditLogService(db)
    item = await service.get_audit_log(audit_id)
    return build_response(data=AuditLogResponse.model_validate(item))


@router.get("/by-entity/{table_name}/{record_id}", summary="Get audit logs for a specific entity")
async def get_audit_logs_by_entity(
    table_name: str,
    record_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    service = AuditLogService(db)
    items = await service.get_by_entity(table_name, record_id)
    return build_response(data=[AuditLogResponse.model_validate(a) for a in items])


@router.get("/by-action/{action}", summary="Get audit logs by action type")
async def get_audit_logs_by_action(
    action: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    service = AuditLogService(db)
    items = await service.get_by_action(action)
    return build_response(data=[AuditLogResponse.model_validate(a) for a in items])
