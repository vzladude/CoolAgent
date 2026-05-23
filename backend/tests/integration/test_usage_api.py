from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from uuid import UUID

from app.database import get_db
from app.routers.auth import router as auth_router
from app.routers.usage import router as usage_router
from app.services.usage_service import UsageService


pytestmark = pytest.mark.integration


@pytest.fixture
def usage_app(db_session):
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    app.include_router(usage_router, prefix="/usage")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


async def register_and_login(client: AsyncClient, email: str) -> str:
    password = "super-secret-123"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_usage_summary_requires_bearer_token(usage_app):
    transport = ASGITransport(app=usage_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/usage/summary")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_usage_summary_scopes_to_authenticated_user(usage_app, db_session):
    transport = ASGITransport(app=usage_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token_a = await register_and_login(client, "usage-api-a@example.com")
        token_b = await register_and_login(client, "usage-api-b@example.com")
        user_a = (await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token_a}"},
        )).json()
        user_b = (await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token_b}"},
        )).json()

        await UsageService(db_session, user_id=UUID(user_a["id"])).record_chat_event(
            message_id=None,
            provider="claude",
            model="fake-claude",
            prompt_policy_version="v1",
            cache_status="miss",
            tokens_input=10,
            tokens_output=5,
        )
        await UsageService(db_session, user_id=UUID(user_b["id"])).record_chat_event(
            message_id=None,
            provider="claude",
            model="fake-claude",
            prompt_policy_version="v1",
            cache_status="miss",
            tokens_input=20,
            tokens_output=5,
        )

        summary_a = await client.get(
            "/usage/summary",
            headers={"Authorization": f"Bearer {token_a}"},
        )

    assert summary_a.status_code == 200
    assert summary_a.json()["total_events"] == 1
    assert summary_a.json()["tokens_input"] == 10
    assert summary_a.json()["user_id"] == user_a["id"]
