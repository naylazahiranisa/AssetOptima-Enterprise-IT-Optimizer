"""Comprehensive tests for Software & License Management module."""

import pytest
from httpx import AsyncClient
from pytest_asyncio import fixture as pytest_asyncio_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.password import hash_password
from app.security.permissions import Role

AUTH_HEADER = "Authorization"


def bearer(token: str) -> dict:
    return {AUTH_HEADER: f"Bearer {token}"}


@pytest_asyncio_fixture
async def _seed_users(db_session: AsyncSession):
    users = [
        ("super@test.com", "Super@123", "Super Admin", Role.SUPER_ADMIN),
        ("manager@test.com", "Manager@123", "IT Manager", Role.IT_MANAGER),
        ("support@test.com", "Support@123", "IT Support", Role.IT_SUPPORT),
    ]
    for email, pwd, name, role in users:
        db_session.add(User(
            email=email, hashed_password=hash_password(pwd),
            full_name=name, role=role, is_active=True,
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


# ==================================================================
# 401 – UNAUTHENTICATED
# ==================================================================

class TestUnauthenticated:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,method", [
        ("/software-categories", "get"),
        ("/software-categories/foo", "get"),
        ("/software-categories", "post"),
        ("/software-categories/foo", "put"),
        ("/software-categories/foo", "delete"),
        ("/software", "get"),
        ("/software/foo", "get"),
        ("/software", "post"),
        ("/software/foo", "put"),
        ("/software/foo", "delete"),
        ("/software/licenses", "get"),
        ("/software/licenses/foo", "get"),
        ("/software/licenses", "post"),
        ("/software/licenses/foo", "put"),
        ("/software/licenses/foo", "delete"),
        ("/software/licenses/expiring", "get"),
        ("/software/licenses/available", "get"),
        ("/software/licenses/unused", "get"),
        ("/software/licenses/cost/summary", "get"),
        ("/software/assignments", "get"),
        ("/software/assignments/assign", "post"),
        ("/software/assignments/remove/foo", "post"),
        ("/software/assignments/transfer", "post"),
        ("/software/usage/logs", "get"),
        ("/software/usage/logs", "post"),
        ("/software/usage/logs/foo", "put"),
        ("/software/usage/top", "get"),
        ("/software/usage/inactive", "get"),
    ])
    async def test_unauthenticated_returns_401(self, client, endpoint, method):
        resp = await getattr(client, method)(endpoint)
        assert resp.status_code == 401


# ==================================================================
# SOFTWARE CATEGORY CRUD
# ==================================================================

class TestSoftwareCategoryCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await client.post("/software-categories", json={"code": "DEV", "name": "Development"}, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["code"] == "DEV"
        assert resp.json()["data"]["name"] == "Development"

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, client, super_token):
        await client.post("/software-categories", json={"code": "DUP", "name": "First"}, headers=bearer(super_token))
        resp = await client.post("/software-categories", json={"code": "DUP", "name": "Second"}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, client, super_token):
        await client.post("/software-categories", json={"code": "DN1", "name": "UniqueName"}, headers=bearer(super_token))
        resp = await client.post("/software-categories", json={"code": "DN2", "name": "UniqueName"}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token):
        cr = await client.post("/software-categories", json={"code": "GET", "name": "GetTest"}, headers=bearer(super_token))
        cid = cr.json()["data"]["id"]
        resp = await client.get(f"/software-categories/{cid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_not_found(self, client, super_token):
        resp = await client.get("/software-categories/00000000-0000-0000-0000-000000000000", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update(self, client, super_token):
        cr = await client.post("/software-categories", json={"code": "UPD", "name": "Before"}, headers=bearer(super_token))
        cid = cr.json()["data"]["id"]
        resp = await client.put(f"/software-categories/{cid}", json={"name": "After"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "After"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token):
        cr = await client.post("/software-categories", json={"code": "DEL", "name": "Delete"}, headers=bearer(super_token))
        cid = cr.json()["data"]["id"]
        await client.delete(f"/software-categories/{cid}", headers=bearer(super_token))
        resp = await client.get(f"/software-categories/{cid}", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token):
        for i in range(3):
            await client.post("/software-categories", json={"code": f"PG{i}", "name": f"Cat{i}"}, headers=bearer(super_token))
        resp = await client.get("/software-categories?per_page=2", headers=bearer(super_token))
        assert len(resp.json()["data"]) <= 2

    @pytest.mark.asyncio
    async def test_manager_cannot_create(self, client, manager_token):
        resp = await client.post("/software-categories", json={"code": "MGR", "name": "Mgr"}, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_can_create(self, client, support_token):
        resp = await client.post("/software-categories", json={"code": "SUP", "name": "Support"}, headers=bearer(support_token))
        assert resp.status_code == 201


# ==================================================================
# SOFTWARE CRUD
# ==================================================================

class TestSoftwareCRUD:
    @pytest_asyncio_fixture
    async def cat_id(self, client, super_token):
        resp = await client.post("/software-categories", json={"code": "SOFTCAT", "name": "Software"}, headers=bearer(super_token))
        return resp.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_create(self, client, super_token, cat_id):
        resp = await client.post("/software", json={
            "name": "Microsoft Office",
            "category_id": cat_id,
            "license_type": "subscription",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["name"] == "Microsoft Office"

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, client, super_token, cat_id):
        await client.post("/software", json={"name": "DupeSoft", "category_id": cat_id}, headers=bearer(super_token))
        resp = await client.post("/software", json={"name": "DupeSoft", "category_id": cat_id}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token, cat_id):
        cr = await client.post("/software", json={"name": "GetSoft", "category_id": cat_id}, headers=bearer(super_token))
        sid = cr.json()["data"]["id"]
        resp = await client.get(f"/software/{sid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update(self, client, super_token, cat_id):
        cr = await client.post("/software", json={"name": "UpdSoft", "category_id": cat_id}, headers=bearer(super_token))
        sid = cr.json()["data"]["id"]
        resp = await client.put(f"/software/{sid}", json={"current_version": "v2.0"}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["current_version"] == "v2.0"

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token, cat_id):
        cr = await client.post("/software", json={"name": "DelSoft", "category_id": cat_id}, headers=bearer(super_token))
        sid = cr.json()["data"]["id"]
        await client.delete(f"/software/{sid}", headers=bearer(super_token))
        resp = await client.get(f"/software/{sid}", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_filter_by_category(self, client, super_token, cat_id):
        resp = await client.get(f"/software?category_id={cat_id}", headers=bearer(super_token))
        assert resp.status_code == 200


# ==================================================================
# LICENSE CRUD
# ==================================================================

class TestLicenseCRUD:
    @pytest_asyncio_fixture
    async def soft_id(self, client, super_token):
        cat_resp = await client.post("/software-categories", json={"code": "LICCAT", "name": "LicenseCat"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        sw = await client.post("/software", json={"name": "LicensedSoft", "category_id": cat_id}, headers=bearer(super_token))
        return sw.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_create(self, client, super_token, soft_id):
        resp = await client.post("/software/licenses", json={
            "license_key": "LIC-001",
            "software_id": soft_id,
            "max_seats": 10,
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["license_key"] == "LIC-001"
        assert resp.json()["data"]["max_seats"] == 10
        assert resp.json()["data"]["allocated_seats"] == 0

    @pytest.mark.asyncio
    async def test_create_duplicate_key(self, client, super_token, soft_id):
        await client.post("/software/licenses", json={"license_key": "DUPKEY", "software_id": soft_id}, headers=bearer(super_token))
        resp = await client.post("/software/licenses", json={"license_key": "DUPKEY", "software_id": soft_id}, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_invalid_software(self, client, super_token):
        resp = await client.post("/software/licenses", json={
            "license_key": "BADSW", "software_id": "00000000-0000-0000-0000-000000000000",
        }, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update(self, client, super_token, soft_id):
        cr = await client.post("/software/licenses", json={"license_key": "UPDLIC", "software_id": soft_id}, headers=bearer(super_token))
        lid = cr.json()["data"]["id"]
        resp = await client.put(f"/software/licenses/{lid}", json={"max_seats": 20}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["max_seats"] == 20

    @pytest.mark.asyncio
    async def test_delete_soft(self, client, super_token, soft_id):
        cr = await client.post("/software/licenses", json={"license_key": "DELLIC", "software_id": soft_id}, headers=bearer(super_token))
        lid = cr.json()["data"]["id"]
        await client.delete(f"/software/licenses/{lid}", headers=bearer(super_token))
        resp = await client.get(f"/software/licenses/{lid}", headers=bearer(super_token))
        assert resp.status_code == 404


# ==================================================================
# SEAT ALLOCATION BUSINESS RULES
# ==================================================================

class TestSeatAllocation:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/software-categories", json={"code": "SEATCAT", "name": "SeatCat"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        sw = await client.post("/software", json={"name": "SeatSoft", "category_id": cat_id}, headers=bearer(super_token))
        soft_id = sw.json()["data"]["id"]
        lic = await client.post("/software/licenses", json={
            "license_key": "SEATLIC", "software_id": soft_id, "max_seats": 2,
        }, headers=bearer(super_token))
        lic_id = lic.json()["data"]["id"]
        e1 = await client.post("/employees", json={"employee_id": "SEAT1", "full_name": "A", "email": "a@seat.com"}, headers=bearer(super_token))
        e1_id = e1.json()["data"]["id"]
        e2 = await client.post("/employees", json={"employee_id": "SEAT2", "full_name": "B", "email": "b@seat.com"}, headers=bearer(super_token))
        e2_id = e2.json()["data"]["id"]
        e3 = await client.post("/employees", json={"employee_id": "SEAT3", "full_name": "C", "email": "c@seat.com"}, headers=bearer(super_token))
        e3_id = e3.json()["data"]["id"]
        return {"soft_id": soft_id, "lic_id": lic_id, "e1": e1_id, "e2": e2_id, "e3": e3_id}

    @pytest.mark.asyncio
    async def test_assign_increases_allocated(self, client, super_token, setup):
        resp = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        lic_resp = await client.get(f"/software/licenses/{setup['lic_id']}", headers=bearer(super_token))
        assert lic_resp.json()["data"]["allocated_seats"] == 1

    @pytest.mark.asyncio
    async def test_remove_decreases_allocated(self, client, super_token, setup):
        assign = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        aid = assign.json()["data"]["id"]
        await client.post(f"/software/assignments/remove/{aid}", json={}, headers=bearer(super_token))
        lic_resp = await client.get(f"/software/licenses/{setup['lic_id']}", headers=bearer(super_token))
        assert lic_resp.json()["data"]["allocated_seats"] == 0

    @pytest.mark.asyncio
    async def test_seat_overflow_raises_error(self, client, super_token, setup):
        # assign 2 seats (max)
        await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        await client.post("/software/assignments/assign", json={
            "employee_id": setup["e2"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        # 3rd should fail
        resp = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e3"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_transfer_preserves_allocation(self, client, super_token, setup):
        await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        await client.post("/software/assignments/transfer", json={
            "from_employee_id": setup["e1"], "to_employee_id": setup["e2"],
            "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        lic_resp = await client.get(f"/software/licenses/{setup['lic_id']}", headers=bearer(super_token))
        assert lic_resp.json()["data"]["allocated_seats"] == 1


# ==================================================================
# SPECIAL ENDPOINTS
# ==================================================================

class TestSpecialEndpoints:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/software-categories", json={"code": "SPCAT", "name": "Special"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        sw = await client.post("/software", json={"name": "SpecialSoft", "category_id": cat_id}, headers=bearer(super_token))
        soft_id = sw.json()["data"]["id"]
        lic = await client.post("/software/licenses", json={
            "license_key": "SPECIAL", "software_id": soft_id, "max_seats": 5,
        }, headers=bearer(super_token))
        lic_id = lic.json()["data"]["id"]
        return {"soft_id": soft_id, "lic_id": lic_id}

    @pytest.mark.asyncio
    async def test_available_seats(self, client, super_token, setup):
        resp = await client.get("/software/licenses/available", headers=bearer(super_token))
        assert resp.status_code == 200
        ids = [l["id"] for l in resp.json()["data"]]
        assert setup["lic_id"] in ids

    @pytest.mark.asyncio
    async def test_cost_summary(self, client, super_token, setup):
        resp = await client.get("/software/licenses/cost/summary", headers=bearer(super_token))
        assert resp.status_code == 200
        assert "total_monthly_cost" in resp.json()["data"]

    @pytest.mark.asyncio
    async def test_manager_cannot_access_cost_summary(self, client, support_token):
        resp = await client.get("/software/licenses/cost/summary", headers=bearer(support_token))
        assert resp.status_code == 403


# ==================================================================
# SOFTWARE ASSIGNMENT
# ==================================================================

class TestEmployeeSoftware:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/software-categories", json={"code": "ASSCAT", "name": "AssignCat"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        sw = await client.post("/software", json={"name": "AssignSoft", "category_id": cat_id}, headers=bearer(super_token))
        soft_id = sw.json()["data"]["id"]
        await client.post("/software/licenses", json={
            "license_key": "ASSLIC", "software_id": soft_id, "max_seats": 10,
        }, headers=bearer(super_token))
        e1 = await client.post("/employees", json={
            "employee_id": "ASE1", "full_name": "Assign1", "email": "as1@t.com",
        }, headers=bearer(super_token))
        e1_id = e1.json()["data"]["id"]
        e2 = await client.post("/employees", json={
            "employee_id": "ASE2", "full_name": "Assign2", "email": "as2@t.com",
        }, headers=bearer(super_token))
        e2_id = e2.json()["data"]["id"]
        return {"soft_id": soft_id, "e1": e1_id, "e2": e2_id}

    @pytest.mark.asyncio
    async def test_assign(self, client, super_token, setup):
        resp = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["employee_id"] == setup["e1"]

    @pytest.mark.asyncio
    async def test_assign_duplicate(self, client, super_token, setup):
        await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        resp = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_remove(self, client, super_token, setup):
        assign = await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        aid = assign.json()["data"]["id"]
        resp = await client.post(f"/software/assignments/remove/{aid}", json={}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "removed"

    @pytest.mark.asyncio
    async def test_transfer(self, client, super_token, setup):
        await client.post("/software/assignments/assign", json={
            "employee_id": setup["e1"], "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        resp = await client.post("/software/assignments/transfer", json={
            "from_employee_id": setup["e1"], "to_employee_id": setup["e2"],
            "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["employee_id"] == setup["e2"]

    @pytest.mark.asyncio
    async def test_transfer_same_employee(self, client, super_token, setup):
        resp = await client.post("/software/assignments/transfer", json={
            "from_employee_id": setup["e1"], "to_employee_id": setup["e1"],
            "software_id": setup["soft_id"],
        }, headers=bearer(super_token))
        assert resp.status_code == 409


# ==================================================================
# USAGE LOGS
# ==================================================================

class TestUsageLogs:
    @pytest_asyncio_fixture
    async def setup(self, client, super_token):
        cat_resp = await client.post("/software-categories", json={"code": "USGCAT", "name": "UsageCat"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        sw = await client.post("/software", json={"name": "UsageSoft", "category_id": cat_id}, headers=bearer(super_token))
        soft_id = sw.json()["data"]["id"]
        e = await client.post("/employees", json={
            "employee_id": "USG1", "full_name": "Usage1", "email": "usg1@t.com",
        }, headers=bearer(super_token))
        emp_id = e.json()["data"]["id"]
        return {"soft_id": soft_id, "emp_id": emp_id}

    @pytest.mark.asyncio
    async def test_create_log(self, client, super_token, setup):
        resp = await client.post("/software/usage/logs", json={
            "employee_id": setup["emp_id"],
            "software_id": setup["soft_id"],
            "login_time": "2026-07-03T08:00:00",
            "ip_address": "192.168.1.1",
            "os": "Windows 11",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_update_logout(self, client, super_token, setup):
        cr = await client.post("/software/usage/logs", json={
            "employee_id": setup["emp_id"],
            "software_id": setup["soft_id"],
            "login_time": "2026-07-03T09:00:00",
        }, headers=bearer(super_token))
        log_id = cr.json()["data"]["id"]
        resp = await client.put(f"/software/usage/logs/{log_id}", json={
            "logout_time": "2026-07-03T17:00:00",
            "session_duration_seconds": 28800,
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["session_duration_seconds"] == 28800

    @pytest.mark.asyncio
    async def test_list_logs(self, client, super_token, setup):
        await client.post("/software/usage/logs", json={
            "employee_id": setup["emp_id"],
            "software_id": setup["soft_id"],
            "login_time": "2026-07-03T10:00:00",
        }, headers=bearer(super_token))
        resp = await client.get("/software/usage/logs", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


# ==================================================================
# API RESPONSE ENVELOPE
# ==================================================================

class TestAPIResponseEnvelope:
    @pytest.mark.asyncio
    async def test_list_envelope(self, client, super_token):
        resp = await client.get("/software-categories", headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "pagination" in body
        assert "timestamp" in body
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_read_by_all_roles(self, client, super_token, manager_token, support_token):
        cr = await client.post("/software-categories", json={"code": "RALL", "name": "ReadAll"}, headers=bearer(super_token))
        cid = cr.json()["data"]["id"]
        for tok in (super_token, manager_token, support_token):
            resp = await client.get(f"/software-categories/{cid}", headers=bearer(tok))
            assert resp.status_code == 200
