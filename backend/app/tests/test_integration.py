"""Enterprise integration tests covering complete business flows.

Tests combine multiple modules to validate end-to-end business processes.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.password import hash_password
from app.security.permissions import Role

AUTH_HEADER = "Authorization"


def bearer(token: str) -> dict:
    return {AUTH_HEADER: f"Bearer {token}"}


@pytest.fixture
def _seed_users(db_session: AsyncSession):
    """Seed all test users for integration scenarios."""
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
    db_session.commit()
    yield


@pytest.fixture
def seeded(_seed_users):
    yield


@pytest.fixture
async def super_token(client: AsyncClient, seeded):
    resp = await client.post("/auth/login", json={"email": "super@test.com", "password": "Super@123"})
    return resp.json()["access_token"]


# ==================================================================
# BUSINESS FLOW 1: Full Asset Lifecycle
# ==================================================================

class TestFullAssetLifecycle:
    """Complete asset lifecycle: create category → create asset → assign → return → delete."""

    async def _create_company(self, client, token):
        resp = await client.post("/companies", json={"code": "FLW_CORP", "name": "Flow Corp"}, headers=bearer(token))
        return resp.json()["data"]["id"]

    async def _create_department(self, client, token, company_id):
        resp = await client.post("/departments", json={"code": "FLW_DEPT", "name": "Engineering", "company_id": company_id}, headers=bearer(token))
        return resp.json()["data"]["id"]

    async def _create_employee(self, client, token, department_id):
        resp = await client.post("/employees", json={
            "employee_id": "FLW_EMP", "full_name": "Flow User", "email": "flow@test.com",
            "department_id": department_id,
        }, headers=bearer(token))
        return resp.json()["data"]["id"]

    async def _create_category(self, client, token):
        resp = await client.post("/asset-categories", json={"code": "FLW_CAT", "name": "Flow Equipment"}, headers=bearer(token))
        return resp.json()["data"]["id"]

    async def _create_asset(self, client, token, category_id):
        resp = await client.post("/assets", json={
            "asset_code": "FLW-AST-001", "name": "Flow Laptop", "category_id": category_id,
        }, headers=bearer(token))
        return resp.json()["data"]

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, client, super_token):
        # 1. Create master data
        company_id = await self._create_company(client, super_token)
        dept_id = await self._create_department(client, super_token, company_id)
        emp_id = await self._create_employee(client, super_token, dept_id)
        cat_id = await self._create_category(client, super_token)

        # 2. Create asset
        asset = await self._create_asset(client, super_token, cat_id)
        asset_id = asset["id"]
        assert asset["status"] == "available"
        assert asset["qr_value"] is not None

        # 3. Get QR
        qr_resp = await client.get(f"/assets/{asset_id}/qr", headers=bearer(super_token))
        assert qr_resp.status_code == 200
        assert qr_resp.json()["data"]["qr_value"] == asset["qr_value"]

        # 4. Assign asset
        assign_resp = await client.post(f"/assets/{asset_id}/assign", json={
            "employee_id": emp_id, "notes": "Integration test assignment",
        }, headers=bearer(super_token))
        assert assign_resp.status_code == 200
        assert assign_resp.json()["data"]["status"] == "assigned"
        assert assign_resp.json()["data"]["employee_id"] == emp_id

        # 5. Verify asset status changed
        get_resp = await client.get(f"/assets/{asset_id}", headers=bearer(super_token))
        assert get_resp.json()["data"]["status"] == "assigned"
        assert get_resp.json()["data"]["current_employee_id"] == emp_id

        # 6. Return asset
        return_resp = await client.post(f"/assets/{asset_id}/return", json={
            "notes": "Returned after testing", "condition": "good",
        }, headers=bearer(super_token))
        assert return_resp.status_code == 200
        assert return_resp.json()["data"]["status"] == "returned"

        # 7. Verify asset is available
        get_resp = await client.get(f"/assets/{asset_id}", headers=bearer(super_token))
        assert get_resp.json()["data"]["status"] == "available"

        # 8. Check history
        hist_resp = await client.get(f"/assets/{asset_id}/history", headers=bearer(super_token))
        actions = [h["action"] for h in hist_resp.json()["data"]]
        assert "created" in actions
        assert "assigned" in actions
        assert "returned" in actions

        # 9. Check audit logs
        audit_resp = await client.get("/audit-logs?per_page=50", headers=bearer(super_token))
        assert audit_resp.status_code == 200

        # 10. Soft delete
        del_resp = await client.delete(f"/assets/{asset_id}", headers=bearer(super_token))
        assert del_resp.status_code == 200

        get_resp = await client.get(f"/assets/{asset_id}", headers=bearer(super_token))
        assert get_resp.status_code == 404


# ==================================================================
# BUSINESS FLOW 2: Software & License Lifecycle
# ==================================================================

class TestSoftwareLicenseLifecycle:
    """Complete software lifecycle: create category → create software → create license → assign → revoke."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self, client, super_token):
        # 1. Create software category
        cat_resp = await client.post("/software-categories", json={
            "code": "SW_FLW", "name": "Flow Software",
        }, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]

        # 2. Create software
        sw_resp = await client.post("/software", json={
            "name": "FlowSoft Pro", "category_id": cat_id, "license_type": "subscription",
        }, headers=bearer(super_token))
        sw_id = sw_resp.json()["data"]["id"]

        # 3. Create license
        lic_resp = await client.post("/software/licenses", json={
            "license_key": "LIC-FLOW-001", "software_id": sw_id, "max_seats": 5,
            "cost_per_seat_monthly": 10.0,
        }, headers=bearer(super_token))
        lic_id = lic_resp.json()["data"]["id"]
        assert lic_resp.json()["data"]["allocated_seats"] == 0

        # 4. Create employee
        emp_resp = await client.post("/employees", json={
            "employee_id": "SW_EMP", "full_name": "Soft User", "email": "soft@test.com",
        }, headers=bearer(super_token))
        emp_id = emp_resp.json()["data"]["id"]

        # 5. Assign software
        assign_resp = await client.post("/software/assignments/assign", json={
            "employee_id": emp_id, "software_id": sw_id, "license_id": lic_id,
        }, headers=bearer(super_token))
        assert assign_resp.status_code == 200
        assignment_id = assign_resp.json()["data"]["id"]

        # 6. Verify allocated seats
        lic_resp = await client.get(f"/software/licenses/{lic_id}", headers=bearer(super_token))
        assert lic_resp.json()["data"]["allocated_seats"] == 1

        # 7. Create usage log
        log_resp = await client.post("/software/usage/logs", json={
            "employee_id": emp_id, "software_id": sw_id,
            "login_time": "2026-07-04T08:00:00",
        }, headers=bearer(super_token))
        assert log_resp.status_code == 201

        # 8. Remove assignment
        remove_resp = await client.post(f"/software/assignments/remove/{assignment_id}", json={
            "notes": "License reclaimed",
        }, headers=bearer(super_token))
        assert remove_resp.status_code == 200

        # 9. Verify allocation decreased
        lic_resp = await client.get(f"/software/licenses/{lic_id}", headers=bearer(super_token))
        assert lic_resp.json()["data"]["allocated_seats"] == 0

        # 10. Check expiring/available/unused endpoints
        assert (await client.get("/software/licenses/expiring?days=30", headers=bearer(super_token))).status_code == 200
        assert (await client.get("/software/licenses/available", headers=bearer(super_token))).status_code == 200
        assert (await client.get("/software/licenses/unused", headers=bearer(super_token))).status_code == 200


# ==================================================================
# BUSINESS FLOW 3: Notification → Audit Trail Flow
# ==================================================================

class TestNotificationAuditFlow:
    @pytest.mark.asyncio
    async def test_notification_lifecycle(self, client, super_token):
        # 1. Create notification
        create_resp = await client.post("/notifications", json={
            "title": "Flow Notification",
            "message": "Testing notification lifecycle",
            "category": "system",
            "priority": "high",
        }, headers=bearer(super_token))
        assert create_resp.status_code == 201
        nid = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["status"] == "unread"

        # 2. Get unread
        unread_resp = await client.get("/notifications/unread", headers=bearer(super_token))
        ids = [n["id"] for n in unread_resp.json()["data"]]
        assert nid in ids

        # 3. Unread count
        count_resp = await client.get("/notifications/unread/count", headers=bearer(super_token))
        assert count_resp.json()["data"]["total"] >= 1

        # 4. Mark as read
        read_resp = await client.post(f"/notifications/read/{nid}", headers=bearer(super_token))
        assert read_resp.json()["data"]["status"] == "read"

        # 5. Archive
        archive_resp = await client.post(f"/notifications/archive/{nid}", headers=bearer(super_token))
        assert archive_resp.json()["data"]["status"] == "archived"

        # 6. Delete archived
        del_resp = await client.delete(f"/notifications/{nid}", headers=bearer(super_token))
        assert del_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_notification_preferences(self, client, super_token):
        # Create preference
        upsert_resp = await client.put("/notification-preferences/asset", json={
            "email_enabled": True, "push_enabled": False, "min_priority": "high",
        }, headers=bearer(super_token))
        assert upsert_resp.status_code == 200

        # Get preferences
        list_resp = await client.get("/notification-preferences", headers=bearer(super_token))
        assert list_resp.status_code == 200
        categories = [p["category"] for p in list_resp.json()["data"]]
        assert "asset" in categories

        # Delete
        del_resp = await client.delete("/notification-preferences/asset", headers=bearer(super_token))
        assert del_resp.status_code == 200


# ==================================================================
# BUSINESS FLOW 4: User & Role Management
# ==================================================================

class TestUserRoleManagement:
    @pytest.mark.asyncio
    async def test_full_user_lifecycle(self, client, super_token):
        # 1. Create role
        role_resp = await client.post("/roles", json={
            "name": "IntegrationAuditor", "description": "Integration test role",
        }, headers=bearer(super_token))
        assert role_resp.status_code == 201
        role_id = role_resp.json()["data"]["id"]

        # 2. Create user
        user_resp = await client.post("/users", json={
            "email": "integration@test.com", "password": "Int3gration!",
            "full_name": "Integration User", "role": "it_support",
        }, headers=bearer(super_token))
        assert user_resp.status_code == 201
        user_id = user_resp.json()["data"]["id"]
        assert "hashed_password" not in user_resp.json()["data"]

        # 3. Update user
        update_resp = await client.put(f"/users/{user_id}", json={
            "full_name": "Updated Integration User",
        }, headers=bearer(super_token))
        assert update_resp.status_code == 200
        assert update_resp.json()["data"]["full_name"] == "Updated Integration User"

        # 4. Verify the new user can login
        login_resp = await client.post("/auth/login", json={
            "email": "integration@test.com", "password": "Int3gration!",
        })
        assert login_resp.status_code == 200
        new_token = login_resp.json()["access_token"]

        # 5. New user has correct role permissions
        me_resp = await client.get("/auth/me", headers=bearer(new_token))
        assert me_resp.json()["role"] == "it_support"

        # 6. Delete user
        del_resp = await client.delete(f"/users/{user_id}", headers=bearer(super_token))
        assert del_resp.status_code == 200

        # 7. Delete role
        del_role_resp = await client.delete(f"/roles/{role_id}", headers=bearer(super_token))
        assert del_role_resp.status_code == 200


# ==================================================================
# ERROR HANDLING — Negative Flow Tests
# ==================================================================

class TestNegativeFlows:
    @pytest.mark.asyncio
    async def test_assign_to_nonexistent_employee(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "NEG_CAT", "name": "Neg"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "NEG-AST", "name": "Neg Asset", "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        resp = await client.post(f"/assets/{asset_id}/assign", json={
            "employee_id": "00000000-0000-0000-0000-000000000000",
        }, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_duplicate_email_employee(self, client, super_token):
        await client.post("/employees", json={
            "employee_id": "NEG_EMP1", "full_name": "First", "email": "dup@test.com",
        }, headers=bearer(super_token))
        resp = await client.post("/employees", json={
            "employee_id": "NEG_EMP2", "full_name": "Second", "email": "dup@test.com",
        }, headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_with_active_assignment(self, client, super_token):
        cat_resp = await client.post("/asset-categories", json={"code": "NEG_DEL", "name": "NegDel"}, headers=bearer(super_token))
        cat_id = cat_resp.json()["data"]["id"]
        ast_resp = await client.post("/assets", json={
            "asset_code": "NEG-DEL", "name": "Neg Del Asset", "category_id": cat_id,
        }, headers=bearer(super_token))
        asset_id = ast_resp.json()["data"]["id"]
        emp_resp = await client.post("/employees", json={
            "employee_id": "NEG_DEL_EMP", "full_name": "Del Emp", "email": "delemp@test.com",
        }, headers=bearer(super_token))
        emp_id = emp_resp.json()["data"]["id"]
        await client.post(f"/assets/{asset_id}/assign", json={"employee_id": emp_id}, headers=bearer(super_token))
        resp = await client.delete(f"/assets/{asset_id}", headers=bearer(super_token))
        assert resp.status_code == 409
        assert "active assignment" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_invalid_pagination(self, client, super_token):
        resp = await client.get("/assets?page=-1", headers=bearer(super_token))
        assert resp.status_code == 422

        resp = await client.get("/assets?per_page=0", headers=bearer(super_token))
        assert resp.status_code == 422

        resp = await client.get("/assets?per_page=200", headers=bearer(super_token))
        assert resp.status_code == 422
