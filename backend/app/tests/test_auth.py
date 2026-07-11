"""Comprehensive authentication & authorisation tests.

Covers login, token refresh, logout, protected endpoints,
role-based access control, and token expiry.
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from pytest_asyncio import fixture as pytest_asyncio_fixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.jwt import _create_token, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from app.security.password import hash_password
from app.security.permissions import Role

# -------------------------------------------------------------------
# Fixtures — seed test users
# -------------------------------------------------------------------


@pytest_asyncio_fixture
async def _seed_users(db_session: AsyncSession):
    """Insert one user per role for testing."""
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
        User(
            email="inactive@test.com",
            hashed_password=hash_password("Inactive@123"),
            full_name="Deactivated User",
            role=Role.IT_SUPPORT,
            is_active=False,
        ),
    ]
    for u in users:
        db_session.add(u)
    await db_session.commit()


@pytest_asyncio_fixture
async def seeded_db(_seed_users):
    """Marker fixture — ensures users are seeded before test."""
    yield


# ============================== LOGIN ==============================


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seeded_db):
    """Valid credentials return a token pair."""
    payload = {"email": "super@test.com", "password": "Super@123"}
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] > 0
    assert data["role"] == "Super Admin"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seeded_db):
    """Wrong password returns 401."""
    payload = {"email": "super@test.com", "password": "wrong"}
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    """Non-existent email returns 401."""
    payload = {"email": "nobody@test.com", "password": "irrelevant"}
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, seeded_db):
    """Deactivated account returns 401."""
    payload = {"email": "inactive@test.com", "password": "Inactive@123"}
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 401
    assert "deactivated" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_validation_error(client: AsyncClient):
    """Invalid email format returns 422."""
    payload = {"email": "not-an-email", "password": "test"}
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 422


# ============================== REFRESH ==============================


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, seeded_db):
    """A valid refresh token yields a new access token."""
    login_resp = await client.post(
        "/auth/login",
        json={"email": "super@test.com", "password": "Super@123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_refresh_with_access_token(client: AsyncClient, seeded_db):
    """Using an access token as a refresh token should fail."""
    login_resp = await client.post(
        "/auth/login",
        json={"email": "super@test.com", "password": "Super@123"},
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_expired_token(client: AsyncClient, seeded_db):
    """An expired refresh token should be rejected."""
    expired = _create_token(
        subject="00000000-0000-0000-0000-000000000000",
        email="expired@test.com",
        role="it_support",
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(seconds=-1),
    )
    resp = await client.post("/auth/refresh", json={"refresh_token": expired})
    assert resp.status_code == 401


# ============================== LOGOUT ==============================


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient, seeded_db):
    """After logout, the same refresh token cannot be used again."""
    login_resp = await client.post(
        "/auth/login",
        json={"email": "super@test.com", "password": "Super@123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 200

    refresh_resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401


# ============================== UNAUTHORIZED ==============================


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    """Accessing /auth/me without a Bearer token returns 401."""
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient):
    """Accessing /auth/me with a bogus token returns 401."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_token(client: AsyncClient, seeded_db):
    """An expired access token returns 401."""
    expired = _create_token(
        subject="00000000-0000-0000-0000-000000000000",
        email="expired@test.com",
        role="it_support",
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(seconds=-60),
    )
    headers = {"Authorization": f"Bearer {expired}"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


# ============================== FORBIDDEN ==============================


@pytest.mark.asyncio
async def test_authenticated_user_can_access_me(client: AsyncClient, seeded_db):
    """A user with valid token can access /auth/me."""
    login_resp = await client.post(
        "/auth/login",
        json={"email": "support@test.com", "password": "Support@123"},
    )
    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200


# ============================== AUTH /ME ==============================


@pytest.mark.asyncio
async def test_me_returns_user(client: AsyncClient, seeded_db):
    """The /auth/me endpoint returns the authenticated user profile."""
    login_resp = await client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "Manager@123"},
    )
    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == "manager@test.com"
    assert data["full_name"] == "IT Manager"
    assert data["role"] == "it_manager"
    assert data["is_active"] is True
    # Ensure password is never exposed
    assert "hashed_password" not in data
    assert "password" not in data


# ============================== UNIT TESTS (no DB) ==============================


class TestPassword:
    def test_hash_and_verify(self):
        from app.security.password import hash_password, verify_password

        pw = "SecurePass!23"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True
        assert verify_password("WrongPass", hashed) is False

    def test_same_password_different_hashes(self):
        from app.security.password import hash_password

        h1 = hash_password("SamePassword")
        h2 = hash_password("SamePassword")
        assert h1 != h2  # bcrypt produces different salts


class TestJWT:
    def test_create_and_decode_access_token(self):
        from app.security.jwt import create_access_token, decode_token

        token = create_access_token(
            subject="user-123",
            email="user@test.com",
            role="it_admin",
        )
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "user@test.com"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(self):
        from app.security.jwt import create_refresh_token, decode_token

        token = create_refresh_token(
            subject="user-456",
            email="refresh@test.com",
            role="it_support",
        )
        payload = decode_token(token)
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"
        assert payload["role"] == "it_support"

    def test_expired_token_raises(self):
        from jose import JWTError
        from app.security.jwt import decode_token, _create_token, ACCESS_TOKEN_TYPE

        expired = _create_token(
            subject="x",
            email="x@test.com",
            role="it_support",
            token_type=ACCESS_TOKEN_TYPE,
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(JWTError):
            decode_token(expired)


class TestPermissions:
    def test_super_admin_has_full_access(self):
        from app.security.permissions import Role, Permission, role_has_permission

        assert role_has_permission(Role.SUPER_ADMIN, Permission.FULL_ACCESS)
        assert role_has_permission(Role.SUPER_ADMIN, Permission.VIEW_DASHBOARD)
        assert role_has_permission(Role.SUPER_ADMIN, Permission.MANAGE_INVENTORY)

    def test_it_manager_permissions(self):
        from app.security.permissions import Role, Permission, role_has_permission

        assert role_has_permission(Role.IT_MANAGER, Permission.VIEW_DASHBOARD)
        assert role_has_permission(Role.IT_MANAGER, Permission.READ_ASSETS)
        assert not role_has_permission(Role.IT_MANAGER, Permission.MANAGE_INVENTORY)
        assert not role_has_permission(Role.IT_MANAGER, Permission.ASSIGN_ASSET)

    def test_it_support_permissions(self):
        from app.security.permissions import Role, Permission, role_has_permission

        assert role_has_permission(Role.IT_SUPPORT, Permission.MANAGE_INVENTORY)
        assert role_has_permission(Role.IT_SUPPORT, Permission.USE_QR_SCANNER)
        assert role_has_permission(Role.IT_SUPPORT, Permission.ASSIGN_ASSET)
        assert role_has_permission(Role.IT_SUPPORT, Permission.RETURN_ASSET)
        assert not role_has_permission(Role.IT_SUPPORT, Permission.VIEW_DASHBOARD)
        assert not role_has_permission(Role.IT_SUPPORT, Permission.READ_ASSETS)

    def test_role_display_names(self):
        from app.security.permissions import ROLE_DISPLAY_NAMES, Role

        assert ROLE_DISPLAY_NAMES[Role.SUPER_ADMIN] == "Super Admin"
        assert ROLE_DISPLAY_NAMES[Role.IT_MANAGER] == "IT Manager"
        assert ROLE_DISPLAY_NAMES[Role.IT_SUPPORT] == "IT Support"
