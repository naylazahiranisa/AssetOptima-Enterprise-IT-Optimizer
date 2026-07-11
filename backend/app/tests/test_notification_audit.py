"""Comprehensive tests for Notification & Audit Logging module."""

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
        ("/notifications", "get"),
        ("/notifications/unread", "get"),
        ("/notifications/unread/count", "get"),
        ("/notifications/foo", "get"),
        ("/notifications", "post"),
        ("/notifications/read/foo", "post"),
        ("/notifications/read-all", "post"),
        ("/notifications/archive/foo", "post"),
        ("/notifications/foo", "delete"),
        ("/notification-preferences", "get"),
        ("/notification-preferences/system", "get"),
        ("/notification-preferences/system", "put"),
        ("/notification-preferences/system", "delete"),
        ("/audit-logs", "get"),
        ("/audit-logs/foo", "get"),
        ("/audit-logs/by-entity/table/id", "get"),
        ("/audit-logs/by-action/create", "get"),
        ("/system-activities", "get"),
        ("/system-activities/recent", "get"),
        ("/system-activities/errors", "get"),
        ("/system-activities/foo", "get"),
        ("/system-activities", "post"),
    ])
    async def test_unauthenticated_returns_401(self, client, endpoint, method):
        resp = await getattr(client, method)(endpoint)
        assert resp.status_code == 401


# ==================================================================
# NOTIFICATIONS — CRUD & SPECIAL ENDPOINTS
# ==================================================================

class TestNotificationCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await client.post("/notifications", json={
            "title": "Test Alert",
            "message": "This is a test notification",
            "category": "system",
            "priority": "medium",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["title"] == "Test Alert"
        assert resp.json()["data"]["status"] == "unread"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, client, super_token):
        resp = await client.post("/notifications", json={
            "title": "Full Alert",
            "message": "Full notification",
            "category": "asset",
            "priority": "high",
            "recipient_role": "it_manager",
            "is_broadcast": True,
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["is_broadcast"] is True

    @pytest.mark.asyncio
    async def test_list(self, client, super_token):
        await client.post("/notifications", json={"title": "List1", "message": "M1"}, headers=bearer(super_token))
        await client.post("/notifications", json={"title": "List2", "message": "M2"}, headers=bearer(super_token))
        resp = await client.get("/notifications", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token):
        for i in range(3):
            await client.post("/notifications", json={"title": f"P{i}", "message": "PM"}, headers=bearer(super_token))
        resp = await client.get("/notifications?per_page=2", headers=bearer(super_token))
        assert len(resp.json()["data"]) <= 2

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token):
        cr = await client.post("/notifications", json={"title": "GetMe", "message": "G"}, headers=bearer(super_token))
        nid = cr.json()["data"]["id"]
        resp = await client.get(f"/notifications/{nid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_not_found(self, client, super_token):
        resp = await client.get("/notifications/00000000-0000-0000-0000-000000000000", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_filter_by_category(self, client, super_token):
        await client.post("/notifications", json={"title": "Cat1", "message": "C1", "category": "asset"}, headers=bearer(super_token))
        resp = await client.get("/notifications?category=asset", headers=bearer(super_token))
        assert all(n["category"] == "asset" for n in resp.json()["data"])

    @pytest.mark.asyncio
    async def test_support_can_create(self, client, support_token):
        resp = await client.post("/notifications", json={
            "title": "Support Notif", "message": "SN",
        }, headers=bearer(support_token))
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_manager_cannot_create(self, client, manager_token):
        resp = await client.post("/notifications", json={
            "title": "Mgr Notif", "message": "MN",
        }, headers=bearer(manager_token))
        assert resp.status_code == 403


class TestNotificationSpecialEndpoints:
    @pytest.mark.asyncio
    async def test_get_unread_empty(self, client, super_token):
        resp = await client.get("/notifications/unread", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_unread_with_items(self, client, super_token):
        await client.post("/notifications", json={"title": "Unread1", "message": "U1"}, headers=bearer(super_token))
        await client.post("/notifications", json={"title": "Unread2", "message": "U2"}, headers=bearer(super_token))
        resp = await client.get("/notifications/unread", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2

    @pytest.mark.asyncio
    async def test_unread_count(self, client, super_token):
        await client.post("/notifications", json={"title": "Count1", "message": "C1"}, headers=bearer(super_token))
        resp = await client.get("/notifications/unread/count", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] >= 1

    @pytest.mark.asyncio
    async def test_mark_as_read(self, client, super_token):
        cr = await client.post("/notifications", json={"title": "ReadMe", "message": "RM"}, headers=bearer(super_token))
        nid = cr.json()["data"]["id"]
        resp = await client.post(f"/notifications/read/{nid}", json={}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "read"
        assert resp.json()["data"]["read_at"] is not None

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, client, super_token):
        resp = await client.post("/notifications/read/00000000-0000-0000-0000-000000000000", json={}, headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, client, super_token):
        await client.post("/notifications", json={"title": "All1", "message": "A1"}, headers=bearer(super_token))
        await client.post("/notifications", json={"title": "All2", "message": "A2"}, headers=bearer(super_token))
        resp = await client.post("/notifications/read-all", json={}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["marked_read"] >= 2

    @pytest.mark.asyncio
    async def test_archive(self, client, super_token):
        cr = await client.post("/notifications", json={"title": "ArchiveMe", "message": "AM"}, headers=bearer(super_token))
        nid = cr.json()["data"]["id"]
        resp = await client.post(f"/notifications/archive/{nid}", json={}, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "archived"

    @pytest.mark.asyncio
    async def test_delete_archived(self, client, super_token):
        cr = await client.post("/notifications", json={"title": "DeleteMe", "message": "DM"}, headers=bearer(super_token))
        nid = cr.json()["data"]["id"]
        await client.post(f"/notifications/archive/{nid}", json={}, headers=bearer(super_token))
        resp = await client.delete(f"/notifications/{nid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_non_archived_returns_409(self, client, super_token):
        cr = await client.post("/notifications", json={"title": "NoDel", "message": "ND"}, headers=bearer(super_token))
        nid = cr.json()["data"]["id"]
        resp = await client.delete(f"/notifications/{nid}", headers=bearer(super_token))
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_manager_cannot_delete(self, client, manager_token):
        resp = await client.delete("/notifications/00000000-0000-0000-0000-000000000000", headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_delete(self, client, support_token):
        resp = await client.delete("/notifications/00000000-0000-0000-0000-000000000000", headers=bearer(support_token))
        assert resp.status_code == 403


# ==================================================================
# NOTIFICATION PREFERENCES
# ==================================================================

class TestNotificationPreferenceCRUD:
    @pytest.mark.asyncio
    async def test_upsert_create(self, client, super_token):
        resp = await client.put("/notification-preferences/asset", json={
            "email_enabled": True,
            "push_enabled": True,
            "min_priority": "high",
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["category"] == "asset"
        assert resp.json()["data"]["min_priority"] == "high"

    @pytest.mark.asyncio
    async def test_upsert_update(self, client, super_token):
        await client.put("/notification-preferences/asset", json={
            "email_enabled": True, "push_enabled": True,
        }, headers=bearer(super_token))
        resp = await client.put("/notification-preferences/asset", json={
            "min_priority": "critical",
        }, headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["min_priority"] == "critical"

    @pytest.mark.asyncio
    async def test_get_preferences(self, client, super_token):
        await client.put("/notification-preferences/asset", json={
            "email_enabled": True, "push_enabled": True,
        }, headers=bearer(super_token))
        resp = await client.get("/notification-preferences", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_single_preference(self, client, super_token):
        await client.put("/notification-preferences/software", json={
            "email_enabled": False, "push_enabled": True,
        }, headers=bearer(super_token))
        resp = await client.get("/notification-preferences/software", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["data"]["email_enabled"] is False

    @pytest.mark.asyncio
    async def test_get_preference_not_found(self, client, super_token):
        resp = await client.get("/notification-preferences/nonexistent", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_preference(self, client, super_token):
        await client.put("/notification-preferences/auth", json={
            "email_enabled": True, "push_enabled": True,
        }, headers=bearer(super_token))
        resp = await client.delete("/notification-preferences/auth", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_support_can_upsert(self, client, support_token):
        resp = await client.put("/notification-preferences/system", json={
            "email_enabled": True, "push_enabled": True,
        }, headers=bearer(support_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_support_cannot_delete(self, client, support_token):
        resp = await client.delete("/notification-preferences/system", headers=bearer(support_token))
        assert resp.status_code == 403


# ==================================================================
# AUDIT LOGS — READ ONLY
# ==================================================================

class TestAuditLogReadOnly:
    @pytest.mark.asyncio
    async def test_list(self, client, super_token):
        resp = await client.get("/audit-logs", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, client, super_token):
        resp = await client.get("/audit-logs/00000000-0000-0000-0000-000000000000", headers=bearer(super_token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_pagination(self, client, super_token):
        resp = await client.get("/audit-logs?per_page=5", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) <= 5

    @pytest.mark.asyncio
    async def test_filter_by_action(self, client, super_token):
        resp = await client.get("/audit-logs?action=create", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_by_entity(self, client, super_token):
        resp = await client.get("/audit-logs/by-entity/users/foo", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_by_action(self, client, super_token):
        resp = await client.get("/audit-logs/by-action/login", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_manager_can_read(self, client, manager_token):
        resp = await client.get("/audit-logs", headers=bearer(manager_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_support_cannot_read(self, client, support_token):
        resp = await client.get("/audit-logs", headers=bearer(support_token))
        assert resp.status_code == 403


# ==================================================================
# SYSTEM ACTIVITIES
# ==================================================================

class TestSystemActivityCRUD:
    @pytest.mark.asyncio
    async def test_create(self, client, super_token):
        resp = await client.post("/system-activities", json={
            "event_type": "application_started",
            "title": "App Started",
            "message": "Application started successfully",
            "severity": "info",
            "service_name": "api",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        assert resp.json()["data"]["event_type"] == "application_started"

    @pytest.mark.asyncio
    async def test_create_error_event(self, client, super_token):
        resp = await client.post("/system-activities", json={
            "event_type": "api_error",
            "title": "500 Error",
            "message": "Internal server error on /api/test",
            "severity": "error",
        }, headers=bearer(super_token))
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_list(self, client, super_token):
        resp = await client.get("/system-activities", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_recent(self, client, super_token):
        resp = await client.get("/system-activities/recent", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_errors(self, client, super_token):
        resp = await client.get("/system-activities/errors", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, super_token):
        cr = await client.post("/system-activities", json={
            "event_type": "database_connected", "title": "DB OK",
        }, headers=bearer(super_token))
        sid = cr.json()["data"]["id"]
        resp = await client.get(f"/system-activities/{sid}", headers=bearer(super_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_support_can_create(self, client, support_token):
        resp = await client.post("/system-activities", json={
            "event_type": "application_started", "title": "Started",
        }, headers=bearer(support_token))
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_manager_cannot_create(self, client, manager_token):
        resp = await client.post("/system-activities", json={
            "event_type": "application_started", "title": "Blocked",
        }, headers=bearer(manager_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_filter_by_event_type(self, client, super_token):
        await client.post("/system-activities", json={
            "event_type": "api_error", "title": "Err1",
        }, headers=bearer(super_token))
        resp = await client.get("/system-activities?event_type=api_error", headers=bearer(super_token))
        assert all(a["event_type"] == "api_error" for a in resp.json()["data"])


# ==================================================================
# API RESPONSE ENVELOPE
# ==================================================================

class TestAPIResponseEnvelope:
    @pytest.mark.asyncio
    async def test_list_envelope(self, client, super_token):
        resp = await client.get("/notifications", headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "pagination" in body
        assert "timestamp" in body
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_notification_envelope(self, client, super_token):
        resp = await client.post("/notifications", json={
            "title": "EnvTest", "message": "ET",
        }, headers=bearer(super_token))
        body = resp.json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_audit_log_envelope(self, client, super_token):
        resp = await client.get("/audit-logs", headers=bearer(super_token))
        body = resp.json()
        assert body["success"] is True
        assert "pagination" in body
