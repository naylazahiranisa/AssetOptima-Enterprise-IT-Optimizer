"""Asset CRUD and special endpoints (assign, return, transfer, history, QR)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetQRResponse, AssetResponse, AssetUpdate
from app.schemas.asset_assignment import AssetAssignRequest, AssetAssignmentResponse, AssetReturnRequest, AssetTransferRequest
from app.schemas.asset_history import AssetHistoryResponse
from app.schemas.common import PaginationParams, build_response
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role
from app.services.asset import AssetService

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("",
    summary="List assets",
    description="Returns a paginated list of assets with optional filtering by category, status, condition, department, employee, vendor, and purchase date range.")
async def list_assets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
    category_id: str | None = Query(None, alias="category_id"),
    status: str | None = Query(None, alias="status"),
    condition: str | None = Query(None, alias="condition"),
    vendor_id: str | None = Query(None, alias="vendor_id"),
    current_employee_id: str | None = Query(None, alias="employee_id"),
):
    service = AssetService(db)
    filters = {"is_deleted": False}
    if category_id:
        filters["category_id"] = category_id
    if status:
        filters["status"] = status
    if condition:
        filters["condition"] = condition
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if current_employee_id:
        filters["current_employee_id"] = current_employee_id

    items, meta = await service.list_assets(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
        filters=filters,
    )
    return build_response(
        data=[AssetResponse.model_validate(a) for a in items],
        pagination=meta,
    )


@router.get("/available",
    summary="List available assets",
    description="Returns a paginated list of assets with status 'available' for assignment.")
async def list_available_assets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    keyword: str | None = None,
):
    service = AssetService(db)
    items, meta = await service.get_available_assets(
        PaginationParams(page=page, per_page=per_page, sort_by=sort_by, sort_order=sort_order, keyword=keyword),
    )
    return build_response(
        data=[AssetResponse.model_validate(a) for a in items],
        pagination=meta,
    )


@router.get("/{asset_id}",
    summary="Get asset by ID",
    description="Returns a single asset by its UUID.")
async def get_asset(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    item = await service.get(asset_id)
    if not item or item.is_deleted:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
    return build_response(data=AssetResponse.model_validate(item))


@router.post("", status_code=status.HTTP_201_CREATED,
    summary="Create asset",
    description="Creates a new asset with a generated QR code. Requires Super Admin or IT Support role.")
async def create_asset(
    body: AssetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    item = await service.create_asset(body.model_dump(), user_id=str(current_user.id))
    return build_response(
        data=AssetResponse.model_validate(item),
        message="Asset created",
    )


@router.put("/{asset_id}",
    summary="Update asset",
    description="Updates an existing asset. Requires Super Admin or IT Support role.")
async def update_asset(
    asset_id: str,
    body: AssetUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    item = await service.update_asset(asset_id, body.model_dump(exclude_unset=True), user_id=str(current_user.id))
    return build_response(data=AssetResponse.model_validate(item), message="Asset updated")


@router.delete("/{asset_id}", status_code=status.HTTP_200_OK,
    summary="Delete asset",
    description="Soft-deletes an asset. Cannot delete if asset has active assignment. Requires Super Admin or IT Support role.")
async def delete_asset(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    await service.delete_asset(asset_id, user_id=str(current_user.id))
    return build_response(message="Asset deleted")


@router.post("/{asset_id}/assign",
    status_code=status.HTTP_200_OK,
    summary="Assign asset to employee",
    description="Assigns an available asset to an employee. Creates assignment record and history entry. Requires Super Admin or IT Support role.")
async def assign_asset(
    asset_id: str,
    body: AssetAssignRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    assignment = await service.assign_asset(
        asset_id=asset_id,
        employee_id=body.employee_id,
        assigned_by=str(current_user.id),
        expected_return_date=body.expected_return_date,
        notes=body.notes,
    )
    return build_response(
        data=AssetAssignmentResponse.model_validate(assignment),
        message="Asset assigned successfully",
    )


@router.post("/{asset_id}/return",
    status_code=status.HTTP_200_OK,
    summary="Return asset from employee",
    description="Returns an assigned asset, making it available again. Creates return record and history entry. Requires Super Admin or IT Support role.")
async def return_asset(
    asset_id: str,
    body: AssetReturnRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    assignment = await service.return_asset(
        asset_id=asset_id,
        user_id=str(current_user.id),
        notes=body.notes,
        condition=body.condition,
    )
    return build_response(
        data=AssetAssignmentResponse.model_validate(assignment),
        message="Asset returned successfully",
    )


@router.post("/{asset_id}/transfer",
    status_code=status.HTTP_200_OK,
    summary="Transfer asset between employees",
    description="Transfers an assigned asset from the current employee to another. Closes current assignment and creates a new one. Requires Super Admin or IT Support role.")
async def transfer_asset(
    asset_id: str,
    body: AssetTransferRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    assignment = await service.transfer_asset(
        asset_id=asset_id,
        new_employee_id=body.employee_id,
        user_id=str(current_user.id),
        notes=body.notes,
    )
    return build_response(
        data=AssetAssignmentResponse.model_validate(assignment),
        message="Asset transferred successfully",
    )


@router.get("/{asset_id}/history",
    summary="Get asset history",
    description="Returns the complete history of actions performed on an asset (created, assigned, returned, transferred, etc.).")
async def get_asset_history(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    history = await service.get_asset_history(asset_id)
    return build_response(
        data=[AssetHistoryResponse.model_validate(h) for h in history],
        message="Asset history retrieved",
    )


@router.get("/{asset_id}/qr",
    summary="Get asset QR code data",
    description="Returns QR code information for an asset, including QR value, asset code, name, and status. Designed for Flutter QR scanner integration.")
async def get_asset_qr(
    asset_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    service = AssetService(db)
    asset = await service.get_asset_qr(asset_id)
    return build_response(
        data=AssetQRResponse.model_validate(asset),
        message="Asset QR data retrieved",
    )
