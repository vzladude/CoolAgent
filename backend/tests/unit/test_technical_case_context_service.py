from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.ai.providers.base import ChatResponse
from app.models.technical_case import Message, TechnicalCase
from app.services.technical_case_context_service import (
    RECENT_MESSAGES_TO_KEEP,
    TechnicalCaseContextService,
)


class FakeProvider:
    def __init__(self, should_fail=False):
        self.calls = []
        self.should_fail = should_fail

    async def chat(self, messages, temperature=0.7, max_tokens=2048):
        self.calls.append((messages, temperature, max_tokens))
        if self.should_fail:
            raise RuntimeError("summary failed")
        return ChatResponse(
            content="Resumen tecnico compacto",
            model="fake-summary",
            tokens_input=20,
            tokens_output=8,
        )


class FakeUsage:
    def __init__(self):
        self.events = []

    async def record_chat_event(self, **kwargs):
        self.events.append(kwargs)


class FakeDb:
    def __init__(self):
        self.flush_count = 0

    async def flush(self):
        self.flush_count += 1


def build_case():
    return TechnicalCase(
        id=uuid4(),
        title="Nevera no enfria",
        status="open",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def build_messages(case_id, count):
    return [
        Message(
            id=uuid4(),
            technical_case_id=case_id,
            role="user" if index % 2 == 0 else "assistant",
            content=f"mensaje tecnico {index}",
            created_at=datetime.now(timezone.utc),
        )
        for index in range(count)
    ]


@pytest.mark.asyncio
async def test_context_service_does_not_compact_under_threshold():
    case = build_case()
    messages = build_messages(case.id, 4)
    provider = FakeProvider()
    usage = FakeUsage()
    service = TechnicalCaseContextService(FakeDb(), provider, usage)

    context = await service.prepare_context(case, messages)

    assert provider.calls == []
    assert context.summary is None
    assert context.recent_messages == messages
    assert context.context_fingerprint


@pytest.mark.asyncio
async def test_context_service_compacts_over_message_threshold_and_keeps_recent():
    case = build_case()
    messages = build_messages(case.id, 35)
    provider = FakeProvider()
    usage = FakeUsage()
    db = FakeDb()
    service = TechnicalCaseContextService(db, provider, usage)

    context = await service.prepare_context(case, messages)

    assert provider.calls
    assert case.context_summary == "Resumen tecnico compacto"
    assert case.summary_until_message_id == messages[-RECENT_MESSAGES_TO_KEEP - 1].id
    assert context.summary == "Resumen tecnico compacto"
    assert context.recent_messages == messages[-RECENT_MESSAGES_TO_KEEP:]
    assert usage.events[0]["event_type"] == "context_compaction"
    assert db.flush_count == 1


@pytest.mark.asyncio
async def test_context_service_compacts_over_token_threshold():
    case = build_case()
    messages = build_messages(case.id, 12)
    for message in messages:
        message.content = "x" * 6000
    provider = FakeProvider()
    usage = FakeUsage()
    service = TechnicalCaseContextService(FakeDb(), provider, usage)

    context = await service.prepare_context(case, messages)

    assert provider.calls
    assert context.summary == "Resumen tecnico compacto"
    assert context.recent_messages == messages[-RECENT_MESSAGES_TO_KEEP:]


@pytest.mark.asyncio
async def test_context_service_falls_back_when_compaction_fails():
    case = build_case()
    case.context_summary = "Resumen anterior"
    messages = build_messages(case.id, 35)
    provider = FakeProvider(should_fail=True)
    usage = FakeUsage()
    service = TechnicalCaseContextService(FakeDb(), provider, usage)

    context = await service.prepare_context(case, messages)

    assert context.summary == "Resumen anterior"
    assert context.recent_messages == messages[-RECENT_MESSAGES_TO_KEEP:]
    assert usage.events == []
