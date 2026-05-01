from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.ai.providers.base import ChatResponse
from app.database import get_db
from app.models.technical_case import Message
from app.routers.chat import router as chat_router
from app.services import chat_service as chat_module


pytestmark = pytest.mark.integration


class FakeProvider:
    async def chat(self, *_args, **_kwargs):
        return ChatResponse(
            content="Respuesta",
            model="fake-claude",
            tokens_input=1,
            tokens_output=1,
        )


class FakeRAGService:
    def __init__(self, _db):
        pass


@pytest.fixture
def chat_app(db_session, monkeypatch):
    monkeypatch.setattr(chat_module, "get_ai_provider", lambda: FakeProvider())
    monkeypatch.setattr(chat_module, "RAGService", FakeRAGService)

    app = FastAPI()
    app.include_router(chat_router, prefix="/chat")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.mark.asyncio
async def test_cases_api_create_update_list_and_paginate_messages(chat_app, db_session):
    transport = ASGITransport(app=chat_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/chat/cases",
            json={
                "title": "Nevera Whirlpool no enfria",
                "manufacturer": "Whirlpool",
                "equipment_model": "WRX",
                "category": "refrigeration",
            },
        )
        assert create_response.status_code == 200
        case = create_response.json()

        patch_response = await client.patch(
            f"/chat/cases/{case['id']}",
            json={"status": "closed"},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["status"] == "closed"

        db_session.add(
            Message(
                id=uuid4(),
                technical_case_id=UUID(case["id"]),
                role="user",
                content="No enfria",
                created_at=datetime.now(timezone.utc),
            )
        )
        await db_session.flush()

        list_response = await client.get("/chat/cases")
        assert list_response.status_code == 200
        assert list_response.json()[0]["last_message_at"] is not None

        messages_response = await client.get(
            f"/chat/cases/{case['id']}/messages",
            params={"limit": 10, "offset": 0},
        )
        assert messages_response.status_code == 200
        body = messages_response.json()
        assert body["count"] == 1
        assert body["messages"][0]["technical_case_id"] == case["id"]


@pytest.mark.asyncio
async def test_legacy_conversations_endpoint_still_creates_case(chat_app):
    transport = ASGITransport(app=chat_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chat/conversations",
            json={"title": "Caso legacy"},
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Caso legacy"
