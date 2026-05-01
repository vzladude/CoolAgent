from __future__ import annotations

import json

import pytest

from app.services.cache_service import CachedChatResponse, ResponseCache


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.set_calls = []

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value, ex=None):
        self.values[key] = value
        self.set_calls.append((key, value, ex))
        return True


class FailingRedis:
    async def get(self, _key):
        raise RuntimeError("redis unavailable")

    async def set(self, *_args, **_kwargs):
        raise RuntimeError("redis unavailable")


def test_chat_cache_key_changes_with_policy_context_history_and_knowledge():
    cache = ResponseCache(redis_client=FakeRedis())

    base_key = cache.build_chat_key(
        provider="claude",
        model="haiku",
        prompt_policy_version="v1",
        user_content="Que significa E7?",
        rag_context="Manual Carrier",
    )
    changed_policy = cache.build_chat_key(
        provider="claude",
        model="haiku",
        prompt_policy_version="v2",
        user_content="Que significa E7?",
        rag_context="Manual Carrier",
    )
    changed_context = cache.build_chat_key(
        provider="claude",
        model="haiku",
        prompt_policy_version="v1",
        user_content="Que significa E7?",
        rag_context="Manual Trane",
    )
    changed_history = cache.build_chat_key(
        provider="claude",
        model="haiku",
        prompt_policy_version="v1",
        user_content="Que significa E7?",
        rag_context="Manual Carrier",
        history_fingerprint="different-history",
    )
    changed_knowledge = cache.build_chat_key(
        provider="claude",
        model="haiku",
        prompt_policy_version="v1",
        user_content="Que significa E7?",
        rag_context="Manual Carrier",
        knowledge_fingerprint="different-knowledge",
    )

    assert base_key != changed_policy
    assert base_key != changed_context
    assert base_key != changed_history
    assert base_key != changed_knowledge


@pytest.mark.asyncio
async def test_cache_round_trip_serializes_chat_response():
    redis = FakeRedis()
    cache = ResponseCache(redis_client=redis)
    response = CachedChatResponse(
        content="Respuesta",
        model="fake-claude",
        tokens_input=4,
        tokens_output=6,
    )

    assert await cache.set_chat_response("key", response) is True
    cached = await cache.get_chat_response("key")

    assert cached == response
    assert redis.set_calls[0][2] == cache.ttl_seconds
    assert json.loads(redis.set_calls[0][1])["content"] == "Respuesta"


@pytest.mark.asyncio
async def test_cache_fails_open_when_redis_is_unavailable():
    cache = ResponseCache(redis_client=FailingRedis())

    assert await cache.get_chat_response("key") is None
    assert await cache.set_chat_response(
        "key",
        CachedChatResponse(content="Respuesta", model="fake"),
    ) is False
