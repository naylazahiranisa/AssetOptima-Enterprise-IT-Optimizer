"""Unit tests for service-layer logic with mocked dependencies."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from app.services.asset_service import AssetService
from app.services.software_license_service import SoftwareLicenseService
from app.schemas.asset import AssetCreate
from app.schemas.software import LicenseCreate


# ==================================================================
# AssetService Unit Tests
# ==================================================================

class TestAssetServiceUnit:
    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        repo.list = AsyncMock(return_value=([], 0))
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def mock_audit_repo(self):
        repo = MagicMock()
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repo, mock_audit_repo):
        return AssetService(repository=mock_repo, audit_repository=mock_audit_repo)

    @pytest.mark.asyncio
    async def test_create_asset_success(self, service, mock_repo, mock_audit_repo):
        mock_repo.create.return_value = MagicMock(
            id="123", asset_code="AST-001", name="Test Asset", qr_value="qr_abc",
            status="available",
        )
        data = AssetCreate(asset_code="AST-001", name="Test Asset")
        result = await service.create(data, user_id="user1")
        assert result.id == "123"
        assert result.qr_value is not None
        mock_audit_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_assets_empty(self, service, mock_repo):
        result, total = await service.list(page=1, per_page=20)
        assert result == []
        assert total == 0
        mock_repo.list.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_asset_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = await service.get_by_id("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_asset_triggers_audit(self, service, mock_repo, mock_audit_repo):
        mock_repo.get_by_id.return_value = MagicMock(id="123", status="available")
        mock_repo.delete.return_value = None
        result = await service.delete("123", user_id="user1")
        assert result is None
        mock_audit_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_asset_with_active_assignment_raises(self, service, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(
            id="123", status="assigned", current_employee_id="emp1",
        )
        with pytest.raises(ValueError, match="Cannot delete asset with active assignment"):
            await service.delete("123", user_id="user1")


# ==================================================================
# SoftwareLicenseService Unit Tests
# ==================================================================

class TestSoftwareLicenseServiceUnit:
    @pytest.fixture
    def mock_license_repo(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        repo.list = AsyncMock(return_value=([], 0))
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        return repo

    @pytest.fixture
    def mock_assignment_repo(self):
        repo = MagicMock()
        repo.list = AsyncMock(return_value=([], 0))
        repo.create = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_license_repo, mock_assignment_repo):
        return SoftwareLicenseService(
            license_repository=mock_license_repo,
            assignment_repository=mock_assignment_repo,
        )

    @pytest.mark.asyncio
    async def test_create_license_with_generated_key(self, service, mock_license_repo):
        mock_license_repo.create.return_value = MagicMock(
            id="lic1", license_key="LK-XXXX-XXXX", software_id="sw1",
            max_seats=10, allocated_seats=0, status="active",
        )
        data = LicenseCreate(software_id="sw1", max_seats=10)
        result = await service.create_license(data)
        assert result.allocated_seats == 0
        assert result.status == "active"
        mock_license_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_expiring_licenses_empty(self, service, mock_license_repo):
        mock_license_repo.list.return_value = ([], 0)
        result, total = await service.get_expiring_licenses(days=30)
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_available_licenses(self, service, mock_license_repo):
        mock_license_repo.list.return_value = ([], 0)
        result, total = await service.get_available_licenses()
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_unused_licenses(self, service, mock_license_repo):
        mock_license_repo.list.return_value = ([], 0)
        result, total = await service.get_unused_licenses()
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_assign_software_success(self, service, mock_license_repo, mock_assignment_repo):
        mock_license = MagicMock(id="lic1", allocated_seats=0, max_seats=5, status="active")
        mock_license_repo.get_by_id.return_value = mock_license
        mock_assignment_repo.create.return_value = MagicMock(id="assign1")
        mock_assignment_repo.get_by_id.return_value = MagicMock(id="assign1")
        result = await service.assign_software(
            employee_id="emp1", software_id="sw1", license_id="lic1",
        )
        assert result is not None
        mock_license_repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_assign_software_no_seats_raises(self, service, mock_license_repo):
        mock_license = MagicMock(id="lic1", allocated_seats=5, max_seats=5, status="active")
        mock_license_repo.get_by_id.return_value = mock_license
        with pytest.raises(ValueError, match="No available seats"):
            await service.assign_software(
                employee_id="emp1", software_id="sw1", license_id="lic1",
            )

    @pytest.mark.asyncio
    async def test_remove_assignment_decreases_allocation(self, service, mock_license_repo, mock_assignment_repo):
        mock_license = MagicMock(id="lic1", allocated_seats=1, max_seats=5)
        mock_license_repo.get_by_id.return_value = mock_license
        mock_assignment_repo.get_by_id.return_value = MagicMock(
            id="assign1", license_id="lic1", employee_id="emp1",
        )
        mock_assignment_repo.delete.return_value = None
        result = await service.remove_assignment(assignment_id="assign1")
        assert result is None
        # Verify the allocated seats count was decremented
        assert mock_license.allocated_seats == 0
        mock_license_repo.update.assert_awaited_once()


# ==================================================================
# Edge Cases & Input Validation
# ==================================================================

class TestServiceEdgeCases:
    @pytest.mark.asyncio
    async def test_zero_per_page_defaults(self):
        """Verify service handles page/per_page boundary values."""
        mock_repo = MagicMock()
        mock_repo.list = AsyncMock(return_value=([], 0))
        audit_repo = MagicMock()
        audit_repo.create = AsyncMock()
        service = AssetService(repository=mock_repo, audit_repository=audit_repo)
        result, total = await service.list(page=0, per_page=0)
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_very_large_per_page(self):
        mock_repo = MagicMock()
        mock_repo.list = AsyncMock(return_value=([], 0))
        audit_repo = MagicMock()
        service = AssetService(repository=mock_repo, audit_repository=audit_repo)
        result, total = await service.list(page=1, per_page=9999)
        assert result == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_asset_raises(self):
        mock_repo = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)
        audit_repo = MagicMock()
        service = AssetService(repository=mock_repo, audit_repository=audit_repo)
        with pytest.raises(ValueError, match="not found"):
            await service.delete("nonexistent", user_id="user1")
