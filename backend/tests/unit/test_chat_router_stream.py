from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import chat as chat_router


class FakeChatService:
    def __init__(self, _db):
        pass

    async def stream_message(self, conversation_id, data):
        yield {
            "type": "delta",
            "content": f"stream:{data.content}",
        }
        yield {
            "type": "done",
            "conversation_id": str(conversation_id),
            "message_id": str(uuid4()),
            "model_used": "fake-claude",
            "tokens_used": 3,
            "cache_status": "miss",
            "created_at": "2026-05-01T00:00:00+00:00",
        }


def build_app(monkeypatch):
    monkeypatch.setattr(chat_router, "ChatService", FakeChatService)
    app = FastAPI()
    app.include_router(chat_router.router, prefix="/chat")

    async def override_get_db():
        yield object()

    app.dependency_overrides[get_db] = override_get_db
    return app


def test_websocket_stream_endpoint_sends_delta_and_done(monkeypatch):
    app = build_app(monkeypatch)
    conversation_id = uuid4()

    with TestClient(app) as client:
        with client.websocket_connect(
            f"/chat/conversations/{conversation_id}/messages/stream"
        ) as websocket:
            websocket.send_json({"content": "Que significa E7?"})

            delta = websocket.receive_json()
            done = websocket.receive_json()

    assert delta == {
        "type": "delta",
        "content": "stream:Que significa E7?",
    }
    assert done["type"] == "done"
    assert done["conversation_id"] == str(conversation_id)
    assert done["cache_status"] == "miss"
