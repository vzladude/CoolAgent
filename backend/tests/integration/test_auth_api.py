from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.routers.auth import router as auth_router


pytestmark = pytest.mark.integration


@pytest.fixture
def auth_app(db_session):
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.mark.asyncio
async def test_register_login_and_read_me(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "Tecnico@Example.com",
                "password": "super-secret-123",
                "full_name": "Ricardo Tecnico",
            },
        )
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "tecnico@example.com",
                "password": "super-secret-123",
            },
        )
        token = login_response.json()["access_token"]
        me_response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["email"] == "tecnico@example.com"
    assert registered["full_name"] == "Ricardo Tecnico"
    assert registered["role"] == "technician"
    assert registered["is_active"] is True
    assert "password_hash" not in registered

    assert login_response.status_code == 200
    logged_in = login_response.json()
    assert logged_in["token_type"] == "bearer"
    assert logged_in["expires_in"] > 0
    assert logged_in["user"]["email"] == "tecnico@example.com"
    assert logged_in["user"]["last_login_at"] is not None

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "tecnico@example.com"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first_response = await client.post(
            "/auth/register",
            json={"email": "tech@example.com", "password": "super-secret-123"},
        )
        duplicate_response = await client.post(
            "/auth/register",
            json={"email": "TECH@example.com", "password": "super-secret-123"},
        )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Ya existe un usuario con ese email"


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/register",
            json={"email": "tech@example.com", "password": "super-secret-123"},
        )
        response = await client.post(
            "/auth/login",
            json={"email": "tech@example.com", "password": "wrong-password"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email o password incorrectos"


@pytest.mark.asyncio
async def test_me_requires_bearer_token(auth_app):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token de autenticacion requerido"
