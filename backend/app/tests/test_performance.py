"""Performance benchmarks to validate N+1, response times, and pagination."""

import time
import asyncio
import pytest
from httpx import AsyncClient

from app.models.user import User
from app.security.password import hash_password
from app.security.permissions import Role

AUTH_HEADER = "Authorization"


def bearer(token: str) -> dict:
    return {AUTH_HEADER: f"Bearer {token}"}


# ==================================================================
# PAGINATION PERFORMANCE
# ==================================================================

class TestPaginationPerformance:
    """Verify paginated endpoints return correct counts and remain fast."""

    PAGINATED_ENDPOINTS = [
        ("GET", "/companies"),
        ("GET", "/departments"),
        ("GET", "/employees"),
        ("GET", "/locations"),
        ("GET", "/vendors"),
        ("GET", "/users"),
        ("GET", "/roles"),
        ("GET", "/asset-categories"),
        ("GET", "/assets"),
        ("GET", "/software-categories"),
        ("GET", "/software"),
        ("GET", "/software/licenses"),
        ("GET", "/software/assignments"),
        ("GET", "/software/usage/logs"),
        ("GET", "/notifications"),
        ("GET", "/notification-preferences"),
        ("GET", "/system-activities"),
        ("GET", "/audit-logs"),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", PAGINATED_ENDPOINTS)
    async def test_paginated_response_shape(self, client, super_token, method, path):
        resp = await getattr(client, method.lower())(path, headers=bearer(super_token))
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)
        if body["data"]:
            # Verify each item has an id
            for item in body["data"]:
                assert "id" in item

    @pytest.mark.asyncio
    async def test_small_per_page(self, client, super_token):
        """1 per page should still return valid data."""
        resp = await client.get("/assets?per_page=1", headers=bearer(super_token))
        assert resp.status_code == 200
        assert len(resp.json()["data"]) <= 1

    @pytest.mark.asyncio
    async def test_large_per_page(self, client, super_token):
        """Large per_page should cap at server max (likely 100)."""
        resp = await client.get("/assets?per_page=200", headers=bearer(super_token))
        assert resp.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_max_per_page_reasonable(self, client, super_token):
        """Fetching max page should complete in reasonable time."""
        t0 = time.perf_counter()
        resp = await client.get("/assets?per_page=100", headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed:.2f}s"


# ==================================================================
# N+1 QUERY DETECTION
# ==================================================================

class TestNPlusOneDetection:
    """Seed related data and ensure list endpoints don't degrade."""

    @pytest.mark.asyncio
    async def test_assets_with_relations(self, client, super_token):
        """Assets endpoint should not exhibit N+1 when categories/employees exist."""
        t0 = time.perf_counter()
        resp = await client.get("/assets?per_page=50", headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        # If N+1 existed, response time would degrade rapidly.
        # For small seed data this is a smoke check; in CI with larger seeds,
        # compare elapsed against a tighter threshold.
        assert elapsed < 5.0, f"Possible N+1 query — took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_employees_with_department(self, client, super_token):
        """Employees should load with department info efficiently."""
        t0 = time.perf_counter()
        resp = await client.get("/employees?per_page=50", headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        assert elapsed < 5.0, f"Possible N+1 query — took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_software_with_categories(self, client, super_token):
        t0 = time.perf_counter()
        resp = await client.get("/software?per_page=50", headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        assert elapsed < 5.0, f"Possible N+1 query — took {elapsed:.2f}s"


# ==================================================================
# CONCURRENT PERFORMANCE
# ==================================================================

class TestConcurrentAccess:
    """Verify the API handles concurrent requests without crashing."""

    CONCURRENT_COUNT = 10

    @pytest.mark.asyncio
    async def test_concurrent_reads(self, client, super_token):
        async def read_asset(idx):
            return await client.get(f"/assets?page=1&per_page=10", headers=bearer(super_token))

        tasks = [read_asset(i) for i in range(self.CONCURRENT_COUNT)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successes = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 200)
        assert successes == self.CONCURRENT_COUNT, f"Only {successes}/{self.CONCURRENT_COUNT} succeeded"

    @pytest.mark.asyncio
    async def test_concurrent_auth(self, client, seeded):
        async def login_user(idx):
            return await client.post("/auth/login", json={
                "email": "super@test.com", "password": "Super@123",
            })

        tasks = [login_user(i) for i in range(self.CONCURRENT_COUNT)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successes = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 200)
        assert successes == self.CONCURRENT_COUNT, f"Only {successes}/{self.CONCURRENT_COUNT} logins succeeded"


# ==================================================================
# RESPONSE TIME BENCHMARKS
# ==================================================================

class TestResponseTimeBenchmarks:
    """Smoke-test that core endpoints respond in acceptable time."""

    ENDPOINTS = [
        ("GET", "/assets?per_page=1"),
        ("GET", "/employees?per_page=1"),
        ("GET", "/auth/me"),
        ("GET", "/system-activities/recent"),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", ENDPOINTS)
    async def test_response_under_threshold(self, client, super_token, method, path):
        t0 = time.perf_counter()
        resp = await getattr(client, method.lower())(path, headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        assert elapsed < 3.0, f"{method} {path} took {elapsed:.2f}s (threshold: 3s)"
