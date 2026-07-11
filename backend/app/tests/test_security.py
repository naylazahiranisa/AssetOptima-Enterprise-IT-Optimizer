"""Security-focused tests: RBAC boundary, permission enforcement, token handling."""

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
async def super_token(client, seeded):
    resp = await client.post("/auth/login", json={"email": "super@test.com", "password": "Super@123"})
    return resp.json()["access_token"]


@pytest.fixture
async def manager_token(client, seeded):
    resp = await client.post("/auth/login", json={"email": "manager@test.com", "password": "Manager@123"})
    return resp.json()["access_token"]


@pytest.fixture
async def support_token(client, seeded):
    resp = await client.post("/auth/login", json={"email": "support@test.com", "password": "Support@123"})
    return resp.json()["access_token"]


# ==================================================================
# RBAC BOUNDARY TESTS
# ==================================================================

class TestRBACBoundaries:
    """Verify every role can/cannot access every endpoint correctly."""

    READ_ENDPOINTS = [
        ("GET", "/companies"),
        ("GET", "/departments"),
        ("GET", "/employees"),
        ("GET", "/locations"),
        ("GET", "/vendors"),
        ("GET", "/users"),
        ("GET", "/roles"),
        ("GET", "/asset-categories"),
        ("GET", "/assets"),
        ("GET", "/assets/available"),
        ("GET", "/software-categories"),
        ("GET", "/software"),
        ("GET", "/software/licenses"),
        ("GET", "/software/licenses/expiring?days=30"),
        ("GET", "/software/licenses/available"),
        ("GET", "/software/licenses/unused"),
        ("GET", "/software/assignments"),
        ("GET", "/software/usage/logs"),
        ("GET", "/software/usage/top"),
        ("GET", "/software/usage/inactive"),
        ("GET", "/notifications"),
        ("GET", "/notifications/unread"),
        ("GET", "/notifications/unread/count"),
        ("GET", "/notification-preferences"),
        ("GET", "/system-activities"),
        ("GET", "/system-activities/recent"),
        ("GET", "/system-activities/errors"),
    ]

    WRITE_ENDPOINTS = [
        ("POST", "/companies"),
        ("POST", "/departments"),
        ("POST", "/employees"),
        ("POST", "/locations"),
        ("POST", "/vendors"),
        ("POST", "/users"),
        ("POST", "/roles"),
        ("POST", "/asset-categories"),
        ("POST", "/assets"),
        ("POST", "/software-categories"),
        ("POST", "/software"),
        ("POST", "/software/licenses"),
        ("POST", "/software/assignments/assign"),
    ]

    SUPER_ONLY_ENDPOINTS = [
        ("DELETE", "/companies/foo"),
        ("DELETE", "/departments/foo"),
        ("DELETE", "/employees/foo"),
        ("DELETE", "/locations/foo"),
        ("DELETE", "/vendors/foo"),
        ("DELETE", "/users/foo"),
        ("DELETE", "/roles/foo"),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", READ_ENDPOINTS)
    async def test_all_roles_can_read(self, client, super_token, manager_token, support_token, method, path):
        for tok in (super_token, manager_token, support_token):
            resp = await getattr(client, method.lower())(path, headers=bearer(tok))
            assert resp.status_code in (200, 422), f"{method} {path} failed for token with status {resp.status_code}"  # 422 is ok (invalid ID)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", WRITE_ENDPOINTS)
    async def test_manager_cannot_write(self, client, manager_token, method, path):
        """IT Managers have read-only access — all writes should be 403."""
        resp = await getattr(client, method.lower())(path, json={"code": "TEST", "name": "Test"}, headers=bearer(manager_token))
        assert resp.status_code == 403, f"{method} {path} returned {resp.status_code}, expected 403"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", SUPER_ONLY_ENDPOINTS)
    async def test_only_super_can_delete(self, client, super_token, manager_token, support_token, method, path):
        """Delete operations require SUPER_ADMIN."""
        for tok in (manager_token, support_token):
            resp = await getattr(client, method.lower())(path, headers=bearer(tok))
            assert resp.status_code == 403, f"{method} {path} allowed {tok}"


# ==================================================================
# AUDIT LOG RBAC
# ==================================================================

class TestAuditLogRBAC:
    @pytest.mark.asyncio
    async def test_support_cannot_read_audit_logs(self, client, support_token):
        resp = await client.get("/audit-logs", headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_read_system_activities(self, client, support_token):
        resp = await client.get("/system-activities", headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_manager_can_read_audit_logs(self, client, manager_token):
        resp = await client.get("/audit-logs", headers=bearer(manager_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_super_can_read_audit_logs(self, client, super_token):
        resp = await client.get("/audit-logs", headers=bearer(super_token))
        assert resp.status_code == 200


# ==================================================================
# AI RBAC
# ==================================================================

class TestAISecurityRBAC:
    @pytest.mark.asyncio
    async def test_support_cannot_predict(self, client, support_token):
        resp = await client.post("/ai/predict/licenses", json={}, headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_analytics(self, client, support_token):
        resp = await client.get("/ai/analytics", headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_cannot_anomaly(self, client, support_token):
        resp = await client.post("/ai/anomaly/licenses", json={}, headers=bearer(support_token))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_support_can_chat(self, client, support_token):
        resp = await client.post("/ai/chat", json={"question": "How to assign asset?"}, headers=bearer(support_token))
        assert resp.status_code == 200


# ==================================================================
# TOKEN SECURITY
# ==================================================================

class TestTokenSecurity:
    @pytest.mark.asyncio
    async def test_no_auth_returns_401(self, client):
        resp = await client.get("/assets")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client):
        resp = await client.get("/assets", headers=bearer("invalid.token.here"))
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_token_type_returns_401(self, client, seeded):
        login_resp = await client.post("/auth/login", json={"email": "super@test.com", "password": "Super@123"})
        refresh_token = login_resp.json()["refresh_token"]
        resp = await client.get("/assets", headers=bearer(refresh_token))
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_auth_header(self, client):
        resp = await client.get("/assets", headers={AUTH_HEADER: "NotBearer token"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_auth_header(self, client):
        resp = await client.get("/assets", headers={AUTH_HEADER: ""})
        assert resp.status_code == 401


# ==================================================================
# VALIDATION BOUNDARY TESTS
# ==================================================================

class TestValidationSecurity:
    @pytest.mark.asyncio
    async def test_xss_in_name_field(self, client, super_token):
        resp = await client.post("/companies", json={
            "code": "XSS_TEST",
            "name": "<script>alert('xss')</script>",
        }, headers=bearer(super_token))
        assert resp.status_code == 201
        # Verify the content is stored as-is (frontend must sanitize)
        data = resp.json()["data"]
        assert "<script>" in data["name"]

    @pytest.mark.asyncio
    async def test_sql_injection_in_query(self, client, super_token):
        resp = await client.get("/assets?keyword='; DROP TABLE assets; --", headers=bearer(super_token))
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_long_string_rejected(self, client, super_token):
        resp = await client.post("/companies", json={
            "code": "A" * 300,
            "name": "Too Long Code",
        }, headers=bearer(super_token))
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_pagination(self, client, super_token):
        resp = await client.get("/assets?page=-1&per_page=-1", headers=bearer(super_token))
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_uuid_returns_422_or_404(self, client, super_token):
        resp = await client.get("/assets/not-a-uuid", headers=bearer(super_token))
        assert resp.status_code in (422, 404)
