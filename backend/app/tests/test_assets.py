"""Comprehensive tests for Asset Management module with RBAC, business rules, and CRUD."""

import pytest
from httpx import AsyncClient
from pytest_asyncio import fixture as pytest_asyncio_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.asset_category import AssetCategory
from app.security.password import hash_password
from app.security.permissions import Role

# -------------------------------------------------------------------
# Fixtures – seed test data
# -------------------------------------------------------------------


@pytest_asyncio_fixture
async def _seed_users(db_session: AsyncSession):
    users_data = [
        ("super@test.com", "Super@123", "Super Admin", Role.SUPER_ADMIN),
        ("manager@test.com", "Manager@123", "IT Manager", Role.IT_MANAGER),
        ("support@test.com", "Support@123", "IT Support", Role.IT_SUPPORT),
    ]
    for email, pwd, name, role in users_data:
        db_session.add(User(
            email=email,
            hashed_password=hash_password(pwd),
            full_name=name,
            role=role,
            is_active=True,
        ))
    await db_session.commit()


@pytest_asyncio_fixture
async def seeded_users(_seed_users):
    yield


@pytest_asyncio_fixture
async def super_token(client: AsyncClient, seeded_users):
    resp = await client.post("/auth/login", json={"email": "super@test.com", "password": "Super@123"})
    return resp.json()["access_token"]


@pytest_asyncio_fixture
async def manager_token(client: AsyncClient, seeded_users):
    resp = await client.post("/auth/login", json={"email": "manager@test.com", "password": "Manager@123"})
    return resp.json()["access_token"]


@pytest_asyncio_fixture
async def support_token(client: AsyncClient, seeded_users):
    resp = await client.post("/auth/login", json={"email": "support@test.com", "password": "Support@123"})
    return resp.json()["access_token"]


@pytest_asyncio_fixture
async def _seed_employee(client, super_token):
    resp = await client.post("/employees", json={
        "employee_id": "EMP001",
        "full_name": "John Doe",
        "email": "john@test.com",
    }, headers={"Authorization": f"Bearer {super_token}"})
    return resp.json()["data"]["id"]


AUTH_HEADER = "Authorization"


def bearer(token: str) -> dict:
    return {AUTH_HEADER: f"Bearer {token}"}


# ==================================================================
# HEALTH CHECK
# ==================================================================

class TestHealth:
    @pytest.mark.asyncio
    async def test_get_asset_categories_list(self, client, super_token):
        resp = await client.get("/asset-categories", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_get_assets_list(self, client, super_token):
        resp = await client.get("/assets", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["success"] is True


# ==================================================================
# 401 – UNAUTHENTICATED
# ==================================================================

class TestUnauthenticated:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,method", [
        ("/asset-categories", "get"),
        ("/asset-categories/foo", "get"),
        ("/asset-categories", "post"),
        ("/asset-categories/foo", "put"),
        ("/asset-categories/foo", "delete"),
        ("/assets", "get"),
        ("/assets/available", "get"),
        ("/assets/foo", "get"),
        ("/assets", "post"),
        ("/assets/foo", "put"),
        ("/assets/foo", "delete"),
        ("/assets/foo/assign", "post"),
        ("/assets/foo/return", "post"),
        ("/assets/foo/transfer", "post"),
        ("/assets/foo/history", "get"),
        ("/assets/foo/qr", "get"),
    ])
    async def test_unauthenticated_returns_401(self, client, endpoint, method):
        resp = await getattr(client, method)(endpoint)
        assert resp.status_code == 401


# ==================================================================
# 403 – FORBIDDEN (manager cannot write)
# ==================================================================

class TestForbiddenWrite:
    @pytest.mark.asyncio
    async def test_manager_cannot_create_category(self, client, manager_token, super_token):
        resp = await client.post("/asset-categories", json={"code": "CAT001", "name": "Laptop"}, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_cannot_create_asset(self, client, manager_token, super_token):
        resp = await client.post("/assets", json={"asset_code": "AST001", "name": "Dell Laptop", "category_id": "foo"}, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_can_create_category(self, client, support_token):
        resp = await client.post("/asset-categories", json={"code": "CAT_IT", "name": "IT Equipment"}, headers=bearer(support_token))
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_support_can_create_asset(self, client, support_token):
        resp = await client.post("/asset-categories", json={"code": "CAT_SUP", "name": "Support Cat"}, headers=bearer(support_token))
        cat_id = resp.json()["data"]["id"]
        resp2 = await client.post("/assets", json={
            "asset_code": "AST_SUP001",
            "name": "Support Asset",
            "category_id": cat_id,
        }, headers=bearer(support_token))
        assert resp2.status_code == 201


# ==================================================================
# ASSET CATEGORY CRUD
# ==================================================================

class TestAssetCategoryCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await client.post("/asset-categories", json={"code": "CAT_ELEC", "name": "Electronics"}, headers=bearer(super_token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["code"] == "CAT_ELEC"
        assert data["data"]["name"] == "Electronics"

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await client.post("/asset-categories", json={"code": "CAT_DUP", "name": "First"}, headers=bearer(super_token))
        resp = await client.post("/asset-categories", json={"code": "CAT_DUP", "name": "Second"}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token):
        create_resp = await client.post("/asset-categories", json={"code": "CAT_GET", "name": "Get Test"}, headers=bearer(super_token))
        cid = create_resp.json()["data"]["id"]
        resp = await client.get(f"/asset-categories/{cid}", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["code"] == "CAT_GET"

    @pytest.mark.asyncio
    async def test_get_not_found(self, client, super_token):
        resp = await client.get("/asset-categories/00000000-0000-0000-0000-000000000000", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await client.post("/asset-categories", json={"code": "CAT_UPD", "name": "Before"}, headers=bearer(super_token))
        cid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/asset-categories/{cid}", json={"name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await client.post("/asset-categories", json={"code": "CAT_DEL", "name": "Delete"}, headers=bearer(super_token))
        cid = create_resp.json()["data"]["id"]
        del_resp = await client.delete(f"/asset-categories/{cid}", headers=bearer(super_token))
        assert del_resp.status_code == 200
        get_resp = await client.get(f"/asset-categories/{cid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token):
        for i in range(5):
            await client.post("/asset-categories", json={"code": f"CAT_PG{i:03d}", "name": f"Page {i}"}, headers=bearer(super_token))
        resp = await client.get("/asset-categories?page=1&per_page=3", headers=bearer(super_token))
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) <= 3
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["per_page"] == 3
        assert body["pagination"]["total"] >= 5

    @pytest.mark.asyncio
    async def test_read_returns_200_all_roles(self, client, super_token, manager_token, support_token):
        create_resp = await client.post("/asset-categories", json={"code": "CAT_RD", "name": "Read Check"}, headers=bearer(super_token))
        cid = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/asset-categories/{cid}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# ASSET CRUD
# ==================================================================

class TestAssetCRUD:
    @pytest_asyncio_fixture
    async def category_id(self, client, super_token):
        resp = await client.post("/asset-categories", json={"code": "CAT_AST", "name": "Assets"}, headers=bearer(super_token))
        return resp.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_create(self, client, super_token, category_id):
        resp = await client.post("/assets", json={
            "asset_code": "AST-C001",
            "name": "Dell Latitude 5520",
            "category_id": category_id,
            "serial_number": "SN-001",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["asset_code"] == "AST-C001"
        assert data["name"] == "Dell Latitude 5520"
        assert data["status"] == "available"
        assert data["qr_value"] is not None
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token, category_id):
        await client.post("/assets", json={
            "asset_code": "AST-DUP",
            "name": "First",
            "category_id": category_id,
        }, headers=bearer(super_token))
        resp = await client.post("/assets", json={
            "asset_code": "AST-DUP",
            "name": "Second",
            "category_id": category_id,
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_duplicate_serial(self, client, super_token, category_id):
        await client.post("/assets", json={
            "asset_code": "AST-SD1",
            "name": "First",
            "category_id": category_id,
            "serial_number": "SN-DUP",
        }, headers=bearer(super_token))
        resp = await client.post("/assets", json={
            "asset_code": "AST-SD2",
            "name": "Second",
            "category_id": category_id,
            "serial_number": "SN-DUP",
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token, category_id):
        create_resp = await client.post("/assets", json={
            "asset_code": "AST-UPD",
            "name": "Before",
            "category_id": category_id,
        }, headers=bearer(super_token))
        aid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/assets/{aid}", json={"name": "After", "condition": "fair"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"
        assert resp.json()["data"]["condition"] == "fair"

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, client, super_token):
        resp = await client.put("/assets/00000000-0000-0000-0000-000000000000", json={"name": "Nope"}, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token, category_id):
        create_resp = await client.post("/assets", json={
            "asset_code": "AST-DEL",
            "name": "Delete Me",
            "category_id": category_id,
        }, headers=bearer(super_token))
        aid = create_resp.json()["data"]["id"]
        del_resp = await client.delete(f"/assets/{aid}", headers=bearer(super_token))
        assert del_resp.status_code == 200
        get_resp = await client.get(f"/assets/{aid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token, category_id):
        create_resp = await client.post("/assets", json={
            "asset_code": "AST-GET",
            "name": "Get Test",
            "category_id": category_id,
        }, headers=bearer(super_token))
        aid = create_resp.json()["data"]["id"]
        resp = await client.get(f"/assets/{aid}", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["asset_code"] == "AST-GET"

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token, category_id):
        for i in range(5):
            await client.post("/assets", json={
                "asset_code": f"AST-PG{i:03d}",
                "name": f"Asset {i}",
                "category_id": category_id,
            }, headers=bearer(super_token))
        resp = await client.get("/assets?page=1&per_page=3", headers=bearer(super_token))
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) <= 3
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["per_page"] == 3

    @pytest.mark.asyncio
    async def test_read_returns_200_all_roles(self, client, super_token, manager_token, support_token, category_id):
        create_resp = await client.post("/assets", json={
            "asset_code": "AST-RD",
            "name": "Read Check",
            "category_id": category_id,
        }, headers=bearer(super_token))
        aid = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/assets/{aid}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# ASSET FILTERING
# ==================================================================

class TestAssetFiltering:
    @pytest_asyncio_fixture
    async def setup_data(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_FILT", "name": "Filter"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        await client.post("/assets", json={
            "asset_code": "AST_F1", "name": "Available Asset",
            "category_id": cat_id, "status": "available",
        }, headers=bearer(super_token))
        await client.post("/assets", json={
            "asset_code": "AST_F2", "name": "Assigned Asset",
            "category_id": cat_id, "status": "assigned",
        }, headers=bearer(super_token))
        await client.post("/assets", json={
            "asset_code": "AST_F3", "name": "Maintenance Asset",
            "category_id": cat_id, "status": "maintenance",
        }, headers=bearer(super_token))
        return cat_id

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client, super_token, setup_data):
        resp = await client.get("/assets?status=available", headers=bearer(super_token))
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["status"] == "available"

    @pytest.mark.asyncio
    async def test_filter_by_category(self, client, super_token, setup_data):
        resp = await client.get(f"/assets?category_id={setup_data}", headers=bearer(super_token))
        assert resp.status_code == 200
        for item in resp.json()["data"]:
            assert item["category_id"] == setup_data


# ==================================================================
# ASSIGNMENT / RETURN / TRANSFER BUSINESS RULES
# ==================================================================

class TestAssignmentBusinessRules:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        # category
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_BIZ", "name": "Business"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        # asset
        ast_resp = await client.post("/assets", json={
            "asset_code": "AST-BIZ",
            "name": "Business Asset",
            "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        # employees
        emp1_resp = await client.post("/employees", json={
            "employee_id": "EMP_BIZ1", "full_name": "Alice", "email": "alice@biz.com",
        }, headers=bearer(super_token))
        emp1_id = emp1_resp.json()["data"]["id"]
        emp2_resp = await client.post("/employees", json={
            "employee_id": "EMP_BIZ2", "full_name": "Bob", "email": "bob@biz.com",
        }, headers=bearer(super_token))
        emp2_id = emp2_resp.json()["data"]["id"]
        return {"asset_id": asset_id, "emp1_id": emp1_id, "emp2_id": emp2_id}

    @pytest.mark.asyncio
    async def test_assign_asset(self, client, super_token, setup):
        resp = await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp1_id"],
            "notes": "Initial assignment",
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["employee_id"] == setup["emp1_id"]
        assert data["data"]["status"] == "assigned"

        # verify asset status changed
        ast_resp = await client.get(f"/assets/{setup['asset_id']}", headers=bearer(super_token))
        assert ast_resp.json()["data"]["status"] == "assigned"
        assert ast_resp.json()["data"]["current_employee_id"] == setup["emp1_id"]

    @pytest.mark.asyncio
    async def test_assign_already_assigned_returns_409(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp1_id"],
        }, headers=bearer(super_token))
        resp = await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp2_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_assign_nonexistent_employee_returns_404(self, client, super_token, setup):
        resp = await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": "00000000-0000-0000-0000-000000000000",
        }, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_return_asset(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp1_id"],
        }, headers=bearer(super_token))
        resp = await client.post(f"/assets/{setup['asset_id']}/return", json={
            "notes": "Returned in good condition",
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "returned"

        # verify asset is available
        ast_resp = await client.get(f"/assets/{setup['asset_id']}", headers=bearer(super_token))
        assert ast_resp.json()["data"]["status"] == "available"
        assert ast_resp.json()["data"]["current_employee_id"] is None

    @pytest.mark.asyncio
    async def test_return_available_asset_returns_409(self, client, super_token, setup):
        resp = await client.post(f"/assets/{setup['asset_id']}/return", json={}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_transfer_asset(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp1_id"],
        }, headers=bearer(super_token))
        resp = await client.post(f"/assets/{setup['asset_id']}/transfer", json={
            "employee_id": setup["emp2_id"],
            "notes": "Transfer to Bob",
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["employee_id"] == setup["emp2_id"]
        assert resp.json()["data"]["status"] == "assigned"

        # verify asset now assigned to emp2
        ast_resp = await client.get(f"/assets/{setup['asset_id']}", headers=bearer(super_token))
        assert ast_resp.json()["data"]["current_employee_id"] == setup["emp2_id"]

    @pytest.mark.asyncio
    async def test_transfer_available_asset_returns_409(self, client, super_token, setup):
        resp = await client.post(f"/assets/{setup['asset_id']}/transfer", json={
            "employee_id": setup["emp2_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_assign_then_return_then_reassign(self, client, super_token, setup):
        # assign
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp1_id"],
        }, headers=bearer(super_token))
        # return
        await client.post(f"/assets/{setup['asset_id']}/return", json={}, headers=bearer(super_token))
        # reassign
        resp = await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp2_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["employee_id"] == setup["emp2_id"]


# ==================================================================
# ASSET HISTORY
# ==================================================================

class TestAssetHistory:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_HIST", "name": "History"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "AST-HIST", "name": "History Asset", "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        emp_resp = await client.post("/employees", json={
            "employee_id": "EMP_HIST", "full_name": "Hist", "email": "hist@test.com",
        }, headers=bearer(super_token))
        emp_id = emp_resp.json()["data"]["id"]
        return {"asset_id": asset_id, "emp_id": emp_id}

    @pytest.mark.asyncio
    async def test_history_after_create(self, client, super_token, setup):
        resp = await client.get(f"/assets/{setup['asset_id']}/history", headers=bearer(super_token))
        assert resp.status_code == 200
        actions = [h["action"] for h in resp.json()["data"]]
        assert "created" in actions

    @pytest.mark.asyncio
    async def test_history_after_assign_and_return(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp_id"],
        }, headers=bearer(super_token))
        await client.post(f"/assets/{setup['asset_id']}/return", json={}, headers=bearer(super_token))
        resp = await client.get(f"/assets/{setup['asset_id']}/history", headers=bearer(super_token))
        assert resp.status_code == 200
        actions = [h["action"] for h in resp.json()["data"]]
        assert "assigned" in actions
        assert "returned" in actions

    @pytest.mark.asyncio
    async def test_history_after_transfer(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp_id"],
        }, headers=bearer(super_token))
        emp2_resp = await client.post("/employees", json={
            "employee_id": "EMP_HIST2", "full_name": "Hist2", "email": "hist2@test.com",
        }, headers=bearer(super_token))
        emp2_id = emp2_resp.json()["data"]["id"]
        await client.post(f"/assets/{setup['asset_id']}/transfer", json={
            "employee_id": emp2_id,
        }, headers=bearer(super_token))
        resp = await client.get(f"/assets/{setup['asset_id']}/history", headers=bearer(super_token))
        assert resp.status_code == 200
        actions = [h["action"] for h in resp.json()["data"]]
        assert "transferred" in actions


# ==================================================================
# QR CODE
# ==================================================================

class TestAssetQR:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_QR", "name": "QR"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "AST-QR01", "name": "QR Asset", "category_id": cat_id,
        }, headers=bearer(super_token))
        return ast_resp.json()["data"]

    @pytest.mark.asyncio
    async def test_get_qr(self, client, super_token, setup):
        resp = await client.get(f"/assets/{setup['id']}/qr", headers=bearer(super_token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["qr_value"] == setup["qr_value"]
        assert data["asset_code"] == setup["asset_code"]
        assert data["name"] == setup["name"]
        assert data["status"] == setup["status"]

    @pytest.mark.asyncio
    async def test_qr_unique_per_asset(self, client, super_token, setup):
        assert setup["qr_value"].startswith("QR-")
        assert len(setup["qr_value"]) > 5

    @pytest.mark.asyncio
    async def test_qr_all_roles_can_access(self, client, super_token, manager_token, support_token, setup):
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/assets/{setup['id']}/qr", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# AVAILABLE ASSETS ENDPOINT
# ==================================================================

class TestAvailableAssets:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_AVAIL", "name": "Avail"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "AST-AVAIL", "name": "Available", "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        emp_resp = await client.post("/employees", json={
            "employee_id": "EMP_AVAIL", "full_name": "Avail", "email": "avail@test.com",
        }, headers=bearer(super_token))
        emp_id = emp_resp.json()["data"]["id"]
        return {"asset_id": asset_id, "emp_id": emp_id, "cat_id": cat_id}

    @pytest.mark.asyncio
    async def test_available_list(self, client, super_token, setup):
        resp = await client.get("/assets/available", headers=bearer(super_token))
        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()["data"]]
        assert setup["asset_id"] in ids

    @pytest.mark.asyncio
    async def test_available_excludes_assigned(self, client, super_token, setup):
        await client.post(f"/assets/{setup['asset_id']}/assign", json={
            "employee_id": setup["emp_id"],
        }, headers=bearer(super_token))
        resp = await client.get("/assets/available", headers=bearer(super_token))
        ids = [a["id"] for a in resp.json()["data"]]
        assert setup["asset_id"] not in ids


# ==================================================================
# API RESPONSE ENVELOPE
# ==================================================================

class TestAPIResponseEnvelope:
    @pytest.mark.asyncio
    async def test_list_returns_envelope(self, client, super_token):
        resp = await client.get("/asset-categories", headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "pagination" in body
        assert "timestamp" in body
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_asset_list_returns_envelope(self, client, super_token):
        resp = await client.get("/assets", headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "pagination" in body
        assert "timestamp" in body

    @pytest.mark.asyncio
    async def test_assign_returns_envelope(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "CAT_ENV", "name": "Envelope"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "AST-ENV", "name": "Env Asset", "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        emp_resp = await client.post("/employees", json={
            "employee_id": "EMP_ENV", "full_name": "Env", "email": "env@test.com",
        }, headers=bearer(super_token))
        emp_id = emp_resp.json()["data"]["id"]
        resp = await client.post(f"/assets/{asset_id}/assign", json={"employee_id": emp_id}, headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert body["success"] is True
