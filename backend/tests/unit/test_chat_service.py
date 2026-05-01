from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.ai.providers.base import ChatResponse
from app.models.conversation import Conversation
from app.schemas.chat import ChatMessageRequest
from app.services import chat_service as chat_module


class FakeProvider:
    def __init__(self):
        self.messages = None

    async def chat(self, messages, temperature=0.7, max_tokens=2048):
        self.messages = messages
        return ChatResponse(
            content="Respuesta usando manual",
            model="fake-claude",
            tokens_input=10,
            tokens_output=5,
        )


class FakeRAGService:
    def __init__(self, _db):
        pass

    async def build_context(self, query: str, limit: int = 3, **_kwargs):
        assert "E7" in query
        assert limit == 3
        return "Manual Carrier: E7 indica sensor del evaporador."


class FakeDb:
    def __init__(self, conversation):
        self.conversation = conversation
        self.added = []
        self.flush_count = 0

    async def get(self, _model, _id):
        return self.conversation

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_count += 1


@pytest.mark.asyncio
async def test_send_message_injects_rag_context_and_uses_mocked_ai(monkeypatch):
    provider = FakeProvider()
    monkeypatch.setattr(chat_module, "get_ai_provider", lambda: provider)
    monkeypatch.setattr(chat_module, "RAGService", FakeRAGService)
    conversation_id = uuid4()
    conversation = Conversation(
        id=conversation_id,
        title="Prueba",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    service = chat_module.ChatService(FakeDb(conversation))

    async def fake_history(_conversation_id):
        return []

    monkeypatch.setattr(service, "_get_conversation_history", fake_history)

    response = await service.send_message(
        conversation_id,
        ChatMessageRequest(content="Que significa E7 en Carrier 38AKS?"),
    )

    assert response.content == "Respuesta usando manual"
    assert response.model_used == "fake-claude"
    assert response.tokens_used == 15
    assert provider.messages[0].role == "system"
    assert "Manual Carrier: E7" in provider.messages[0].content
