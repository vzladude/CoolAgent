"""
Redis-backed cache for chat responses.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from redis.asyncio import Redis

from app.config import get_settings


@dataclass(frozen=True)
class CachedChatResponse:
    content: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0


class ResponseCache:
    """Exact-match cache for chat responses.

    The key includes prompt policy and RAG context hash so old answers are not
    reused when the assistant rules or retrieved documentation change.
    """

    def __init__(self, redis_client: Redis | None = None):
        self.settings = get_settings()
        self.enabled = self.settings.chat_cache_enabled
        self.ttl_seconds = self.settings.chat_cache_ttl_seconds
        self.namespace = self.settings.cache_namespace
        self._redis = redis_client

    def build_chat_key(
        self,
        *,
        provider: str,
        model: str,
        prompt_policy_version: str,
        user_content: str,
        rag_context: str | None,
        history_fingerprint: str | None = None,
    ) -> str:
        context_hash = hashlib.sha256((rag_context or "").encode("utf-8")).hexdigest()
        payload = {
            "kind": "chat_exact",
            "provider": provider,
            "model": model,
            "prompt_policy_version": prompt_policy_version,
            "user_content": " ".join(user_content.split()),
            "rag_context_hash": context_hash,
            "history_fingerprint": history_fingerprint or "",
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{self.namespace}:chat:{digest}"

    async def get_chat_response(self, key: str) -> CachedChatResponse | None:
        if not self.enabled:
            return None
        try:
            cached = await self._client().get(key)
        except Exception:
            return None

        if not cached:
            return None

        try:
            payload = json.loads(cached)
            return CachedChatResponse(
                content=payload["content"],
                model=payload["model"],
                tokens_input=int(payload.get("tokens_input", 0)),
                tokens_output=int(payload.get("tokens_output", 0)),
            )
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            return None

    async def set_chat_response(
        self,
        key: str,
        response: CachedChatResponse,
    ) -> bool:
        if not self.enabled:
            return False
        try:
            await self._client().set(
                key,
                json.dumps(asdict(response), sort_keys=True),
                ex=self.ttl_seconds,
            )
            return True
        except Exception:
            return False

    def _client(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis
