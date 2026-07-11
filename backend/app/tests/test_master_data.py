"""Comprehensive tests for all Core Master Data CRUD endpoints with RBAC."""

import pytest
from httpx import AsyncClient
from pytest_asyncio import fixture as pytest_asyncio_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.password import hash_password
from app.security.permissions import Role

# -------------------------------------------------------------------
# Fixtures – seed test data
# -------------------------------------------------------------------


@pytest_asyncio_fixture
async def _seed_users(db_session: AsyncSession):
    users = [
        User(
            email="super@test.com",
            hashed_password=hash_password("Super@123"),
            full_name="Super Admin",
            role=Role.SUPER_ADMIN,
            is_active=True,
        ),
        User(
            email="manager@test.com",
            hashed_password=hash_password("Manager@123"),
            full_name="IT Manager",
            role=Role.IT_MANAGER,
            is_active=True,
        ),
        User(
            email="support@test.com",
            hashed_password=hash_password("Support@123"),
            full_name="IT Support",
            role=Role.IT_SUPPORT,
            is_active=True,
        ),
    ]
    for u in users:
        db_session.add(u)
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


# ---------- helpers ----------

AUTH_HEADER = "Authorization"


def bearer(token: str) -> dict:
    return {AUTH_HEADER: f"Bearer {token}"}


async def _create_company(client, token, code="C001", name="Test Corp"):
    resp = await client.post("/companies", json={"code": code, "name": name}, headers=bearer(token))
    return resp


async def _create_dept(client, token, code="D001", name="Engineering"):
    resp = await client.post("/departments", json={"code": code, "name": name}, headers=bearer(token))
    return resp


async def _create_employee(client, token, employee_id="EMP001", full_name="John Doe", email="john@test.com"):
    resp = await client.post("/employees", json={"employee_id": employee_id, "full_name": full_name, "email": email}, headers=bearer(token))
    return resp


async def _create_role(client, token, name="Developer", description="Developer role"):
    resp = await client.post("/roles", json={"name": name, "description": description}, headers=bearer(token))
    return resp


async def _create_user(client, token, email="newuser@test.com", password="Pass1234", full_name="New User", role="it_support"):
    resp = await client.post("/users", json={"email": email, "password": password, "full_name": full_name, "role": role}, headers=bearer(token))
    return resp


async def _create_location(client, token, code="LOC001", name="HQ"):
    resp = await client.post("/locations", json={"code": code, "name": name}, headers=bearer(token))
    return resp


async def _create_vendor(client, token, code="V001", name="Acme Corp"):
    resp = await client.post("/vendors", json={"code": code, "name": name}, headers=bearer(token))
    return resp


# ==================================================================
# 401 – UNAUTHENTICATED
# ==================================================================


class TestUnauthenticated:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,method", [
        ("/companies", "get"),
        ("/companies/foo", "get"),
        ("/companies", "post"),
        ("/companies/foo", "put"),
        ("/companies/foo", "delete"),
        ("/departments", "get"),
        ("/departments/foo", "get"),
        ("/departments", "post"),
        ("/departments/foo", "put"),
        ("/departments/foo", "delete"),
        ("/employees", "get"),
        ("/employees/foo", "get"),
        ("/employees", "post"),
        ("/employees/foo", "put"),
        ("/employees/foo", "delete"),
        ("/roles", "get"),
        ("/roles/foo", "get"),
        ("/roles", "post"),
        ("/roles/foo", "put"),
        ("/roles/foo", "delete"),
        ("/users", "get"),
        ("/users/foo", "get"),
        ("/users", "post"),
        ("/users/foo", "put"),
        ("/users/foo", "delete"),
        ("/locations", "get"),
        ("/locations/foo", "get"),
        ("/locations", "post"),
        ("/locations/foo", "put"),
        ("/locations/foo", "delete"),
        ("/vendors", "get"),
        ("/vendors/foo", "get"),
        ("/vendors", "post"),
        ("/vendors/foo", "put"),
        ("/vendors/foo", "delete"),
    ])
    async def test_unauthenticated_returns_401(self, client, endpoint, method):
        resp = await getattr(client, method)(endpoint)
        assert resp.status_code == 401


# ==================================================================
# 403 – FORBIDDEN (read-only roles cannot write)
# ==================================================================


class TestForbiddenWrite:
    @pytest.mark.asyncio
    async def test_manager_cannot_create(self, client, manager_token, super_token):
        resp = await client.post("/companies", json={"code": "F001", "name": "Nope"}, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_create(self, client, support_token):
        resp = await client.post("/departments", json={"code": "F002", "name": "Nope"}, headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_cannot_update(self, client, manager_token, super_token):
        create_resp = await _create_company(client, super_token, code="UPD403", name="Exists")
        uid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/companies/{uid}", json={"name": "Updated"}, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_update(self, client, support_token, super_token):
        create_resp = await _create_company(client, super_token, code="UPD404", name="Exists2")
        uid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/companies/{uid}", json={"name": "Updated"}, headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_cannot_delete(self, client, manager_token, super_token):
        create_resp = await _create_company(client, super_token, code="DEL403", name="Delete Me")
        uid = create_resp.json()["data"]["id"]
        resp = await client.delete(f"/companies/{uid}", headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_delete(self, client, support_token, super_token):
        create_resp = await _create_company(client, super_token, code="DEL404", name="Delete Me2")
        uid = create_resp.json()["data"]["id"]
        resp = await client.delete(f"/companies/{uid}", headers=bearer(support_token))
        assert resp.status_code == 403


# ==================================================================
# READ – all authenticated roles can read
# ==================================================================


class TestRead:
    @pytest.mark.asyncio
    async def test_list_companies_super(self, client, super_token):
        await _create_company(client, super_token, code="R001", name="Read Test")
        resp = await client.get("/companies", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_list_companies_manager(self, client, manager_token, super_token):
        await _create_company(client, super_token, code="R002", name="Read Test 2")
        resp = await client.get("/companies", headers=bearer(manager_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_companies_support(self, client, support_token, super_token):
        await _create_company(client, super_token, code="R003", name="Read Test 3")
        resp = await client.get("/companies", headers=bearer(support_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_company_super(self, client, super_token):
        create_resp = await _create_company(client, super_token, code="R010", name="Get Test")
        cid = create_resp.json()["data"]["id"]
        resp = await client.get(f"/companies/{cid}", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["code"] == "R010"

    @pytest.mark.asyncio
    async def test_get_company_manager(self, client, manager_token, super_token):
        create_resp = await _create_company(client, super_token, code="R011", name="Get Test M")
        cid = create_resp.json()["data"]["id"]
        resp = await client.get(f"/companies/{cid}", headers=bearer(manager_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_company_support(self, client, support_token, super_token):
        create_resp = await _create_company(client, super_token, code="R012", name="Get Test S")
        cid = create_resp.json()["data"]["id"]
        resp = await client.get(f"/companies/{cid}", headers=bearer(support_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, client, super_token):
        resp = await client.get("/companies/00000000-0000-0000-0000-000000000000", headers=bearer(super_token))
        assert resp.status_code == 404


# ==================================================================
# COMPANY CRUD
# ==================================================================


class TestCompanyCRUD:
    @pytest.mark.asyncio
    async def test_create_company(self, client, super_token):
        resp = await _create_company(client, super_token, code="CC001", name="Create Corp")
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["code"] == "CC001"
        assert data["data"]["name"] == "Create Corp"
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await _create_company(client, super_token, code="DUP001", name="First")
        resp = await _create_company(client, super_token, code="DUP001", name="Second")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update_company(self, client, super_token):
        create_resp = await _create_company(client, super_token, code="UP001", name="Before")
        cid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/companies/{cid}", json={"name": "After", "phone": "123456"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"
        assert resp.json()["data"]["phone"] == "123456"

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, client, super_token):
        resp = await client.put("/companies/00000000-0000-0000-0000-000000000000", json={"name": "Nope"}, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_company_soft(self, client, super_token):
        create_resp = await _create_company(client, super_token, code="SD001", name="Soft Delete")
        cid = create_resp.json()["data"]["id"]
        del_resp = await client.delete(f"/companies/{cid}", headers=bearer(super_token))
        assert del_resp.status_code == 200

        get_resp = await client.get(f"/companies/{cid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token):
        for i in range(5):
            await _create_company(client, super_token, code=f"PG{i:03d}", name=f"Page {i}")
        resp = await client.get("/companies?page=1&per_page=3", headers=bearer(super_token))
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) <= 3
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["per_page"] == 3
        assert body["pagination"]["total"] >= 5


# ==================================================================
# DEPARTMENT CRUD
# ==================================================================


class TestDepartmentCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_dept(client, super_token, code="DC001", name="Engineering")
        assert resp.status_code == 201
        assert resp.json()["data"]["code"] == "DC001"

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await _create_dept(client, super_token, code="DD001", name="First")
        resp = await _create_dept(client, super_token, code="DD001", name="Second")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_dept(client, super_token, code="DU001", name="Before")
        did = create_resp.json()["data"]["id"]
        resp = await client.put(f"/departments/{did}", json={"name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await _create_dept(client, super_token, code="DD02", name="To Delete")
        did = create_resp.json()["data"]["id"]
        await client.delete(f"/departments/{did}", headers=bearer(super_token))
        get_resp = await client.get(f"/departments/{did}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        create_resp = await _create_dept(client, super_token, code="DR001", name="Read Check")
        did = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/departments/{did}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# EMPLOYEE CRUD
# ==================================================================


class TestEmployeeCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_employee(client, super_token, employee_id="E001", full_name="Alice", email="alice@t.com")
        assert resp.status_code == 201
        assert resp.json()["data"]["employee_id"] == "E001"

    @pytest.mark.asyncio
    async def test_create_duplicate_employee_id(self, client, super_token):
        await _create_employee(client, super_token, employee_id="E002", full_name="A", email="a@t.com")
        resp = await _create_employee(client, super_token, employee_id="E002", full_name="B", email="b@t.com")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_duplicate_email(self, client, super_token):
        await _create_employee(client, super_token, employee_id="E003", full_name="X", email="dup@t.com")
        resp = await _create_employee(client, super_token, employee_id="E004", full_name="Y", email="dup@t.com")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_employee(client, super_token, employee_id="E005", full_name="Before", email="before@t.com")
        eid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/employees/{eid}", json={"full_name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["full_name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await _create_employee(client, super_token, employee_id="E006", full_name="Del", email="del@t.com")
        eid = create_resp.json()["data"]["id"]
        await client.delete(f"/employees/{eid}", headers=bearer(super_token))
        get_resp = await client.get(f"/employees/{eid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        create_resp = await _create_employee(client, super_token, employee_id="E007", full_name="R", email="r@t.com")
        eid = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/employees/{eid}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# ROLE CRUD
# ==================================================================


class TestRoleCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_role(client, super_token, name="Tester")
        assert resp.status_code == 201
        assert resp.json()["data"]["name"] == "Tester"

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, client, super_token):
        await _create_role(client, super_token, name="DuplicateRole")
        resp = await _create_role(client, super_token, name="DuplicateRole")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_role(client, super_token, name="Updatable", description="old")
        rid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/roles/{rid}", json={"description": "new desc"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["description"] == "new desc"

    @pytest.mark.asyncio
    async def test_delete(self, client, super_token):
        create_resp = await _create_role(client, super_token, name="ToDelete")
        rid = create_resp.json()["data"]["id"]
        resp = await client.delete(f"/roles/{rid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        resp = await client.get("/roles", headers=bearer(manager_token))
        assert resp.status_code == 200
        resp = await client.get("/roles", headers=bearer(support_token))
        assert resp.status_code == 200


# ==================================================================
# USER CRUD (admin management)
# ==================================================================


class TestUserCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_user(client, super_token, email="newguy@t.com", full_name="New Guy")
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["email"] == "newguy@t.com"
        assert data["full_name"] == "New Guy"
        assert "hashed_password" not in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_create_duplicate_email(self, client, super_token):
        await _create_user(client, super_token, email="dupuser@t.com", full_name="First")
        resp = await _create_user(client, super_token, email="dupuser@t.com", full_name="Second")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_user(client, super_token, email="upduser@t.com", full_name="Before")
        uid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/users/{uid}", json={"full_name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["full_name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await _create_user(client, super_token, email="deluser@t.com", full_name="Delete Me")
        uid = create_resp.json()["data"]["id"]
        await client.delete(f"/users/{uid}", headers=bearer(super_token))
        get_resp = await client.get(f"/users/{uid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        for tok in (super_token, manager_token, support_token):
            resp = await client.get("/users", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# LOCATION CRUD
# ==================================================================


class TestLocationCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_location(client, super_token, code="LC001", name="Warehouse")
        assert resp.status_code == 201
        assert resp.json()["data"]["code"] == "LC001"

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await _create_location(client, super_token, code="LD001", name="First")
        resp = await _create_location(client, super_token, code="LD001", name="Second")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_location(client, super_token, code="LU001", name="Before")
        lid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/locations/{lid}", json={"name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await _create_location(client, super_token, code="LD02", name="To Delete")
        lid = create_resp.json()["data"]["id"]
        await client.delete(f"/locations/{lid}", headers=bearer(super_token))
        get_resp = await client.get(f"/locations/{lid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        create_resp = await _create_location(client, super_token, code="LR001", name="Read")
        lid = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/locations/{lid}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# VENDOR CRUD
# ==================================================================


class TestVendorCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await _create_vendor(client, super_token, code="VC001", name="Supplier")
        assert resp.status_code == 201
        assert resp.json()["data"]["code"] == "VC001"

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await _create_vendor(client, super_token, code="VD001", name="First")
        resp = await _create_vendor(client, super_token, code="VD001", name="Second")
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        create_resp = await _create_vendor(client, super_token, code="VU001", name="Before")
        vid = create_resp.json()["data"]["id"]
        resp = await client.put(f"/vendors/{vid}", json={"name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        create_resp = await _create_vendor(client, super_token, code="VD02", name="To Delete")
        vid = create_resp.json()["data"]["id"]
        await client.delete(f"/vendors/{vid}", headers=bearer(super_token))
        get_resp = await client.get(f"/vendors/{vid}", headers=bearer(super_token))
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_read_returns_200(self, client, super_token, manager_token, support_token):
        create_resp = await _create_vendor(client, super_token, code="VR001", name="Read")
        vid = create_resp.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/vendors/{vid}", headers=bearer(tok))
            assert resp.status_code == 200


# ==================================================================
# API Response Envelope
# ==================================================================


class TestAPIResponseEnvelope:
    @pytest.mark.asyncio
    async def test_list_returns_envelope(self, client, super_token):
        resp = await client.get("/companies", headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "pagination" in body
        assert "timestamp" in body
        assert body["success"] is True
