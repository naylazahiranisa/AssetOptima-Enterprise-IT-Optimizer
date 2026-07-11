"""Smoke tests for health-check endpoints."""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "AssetOptima"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_swagger_docs(client):
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_redoc(client):
    response = await client.get("/redoc")
    assert response.status_code == 200
