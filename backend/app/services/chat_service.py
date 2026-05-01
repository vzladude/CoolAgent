"""
Chat business logic.

This service keeps the order intentional:
1. Domain guard blocks clear out-of-scope questions.
2. RAG retrieves technical context.
3. Redis cache avoids repeating identical Claude calls.
4. Usage tracking records tokens and cache activity.
"""

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts import build_rag_prompt
from app.ai.providers import get_ai_provider
from app.ai.providers.base import ChatMessage
from app.config import get_settings
from app.models.conversation import Conversation, Message
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
)
from app.services.cache_service import CachedChatResponse, ResponseCache
from app.services.domain_guard import DomainGuard, PROMPT_POLICY_VERSION
from app.services.rag_service import RAGService
from app.services.usage_service import UsageService


class ChatService:
    """Service for conversations with the AI assistant."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.provider = get_ai_provider()
        self.rag = RAGService(db)
        self.domain_guard = DomainGuard()
        self.cache = ResponseCache()
        self.usage = UsageService(db)

    async def create_conversation(
        self, data: ConversationCreate
    ) -> ConversationResponse:
        """Create a new conversation."""
        conversation = Conversation(
            id=uuid4(),
            title=data.title or "Nueva conversacion",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(conversation)
        await self.db.flush()

        return ConversationResponse.model_validate(conversation)

    async def send_message(
        self,
        conversation_id: UUID,
        data: ChatMessageRequest,
    ) -> ChatMessageResponse:
        """Send a user message and return an assistant response."""
        conversation = await self.db.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversacion {conversation_id} no encontrada")

        domain_result = self.domain_guard.evaluate(data.content)
        if not domain_result.is_allowed:
            user_message = self._build_user_message(conversation_id, data.content)
            assistant_message = Message(
                id=uuid4(),
                conversation_id=conversation_id,
                role="assistant",
                content=domain_result.response or "",
                tokens_used=0,
                model_used=f"domain-guard:{domain_result.policy_version}",
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(user_message)
            self.db.add(assistant_message)
            await self.usage.record_chat_event(
                conversation_id=conversation_id,
                message_id=assistant_message.id,
                provider="domain_guard",
                model=assistant_message.model_used,
                prompt_policy_version=domain_result.policy_version,
                cache_status="blocked",
            )
            await self.db.flush()
            return ChatMessageResponse.model_validate(assistant_message)

        history = await self._get_conversation_history(conversation_id)

        user_message = self._build_user_message(conversation_id, data.content)
        self.db.add(user_message)

        rag_context = await self.rag.build_context(data.content, limit=3)
        knowledge_fingerprint = await self.rag.knowledge_fingerprint()
        system_prompt = build_rag_prompt(rag_context)

        provider_name = self.settings.ai_provider
        model_name = self._chat_model_name()
        cache_key = self.cache.build_chat_key(
            provider=provider_name,
            model=model_name,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            user_content=data.content,
            rag_context=rag_context,
            history_fingerprint=self._history_fingerprint(history),
            knowledge_fingerprint=knowledge_fingerprint,
        )

        cached_response = await self.cache.get_chat_response(cache_key)
        if cached_response is not None:
            assistant_message = Message(
                id=uuid4(),
                conversation_id=conversation_id,
                role="assistant",
                content=cached_response.content,
                tokens_used=0,
                model_used=f"cache:{cached_response.model}"[:100],
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(assistant_message)
            await self.usage.record_chat_event(
                conversation_id=conversation_id,
                message_id=assistant_message.id,
                provider=provider_name,
                model=cached_response.model,
                prompt_policy_version=PROMPT_POLICY_VERSION,
                cache_status="hit",
            )
            await self.db.flush()
            return ChatMessageResponse.model_validate(assistant_message)

        ai_messages = [
            ChatMessage(role="system", content=system_prompt),
            *[ChatMessage(role=msg.role, content=msg.content) for msg in history],
            ChatMessage(role="user", content=data.content),
        ]

        response = await self.provider.chat(ai_messages)
        tokens_used = response.tokens_input + response.tokens_output

        assistant_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            tokens_used=tokens_used,
            model_used=response.model,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(assistant_message)

        await self.cache.set_chat_response(
            cache_key,
            CachedChatResponse(
                content=response.content,
                model=response.model,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
            ),
        )
        await self.usage.record_chat_event(
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            provider=provider_name,
            model=response.model,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            cache_status="miss",
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
        )
        await self.db.flush()

        return ChatMessageResponse.model_validate(assistant_message)

    async def _get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 20,
    ) -> list[Message]:
        """Get the most recent conversation messages in chronological order."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    def _build_user_message(self, conversation_id: UUID, content: str) -> Message:
        return Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="user",
            content=content,
            created_at=datetime.now(timezone.utc),
        )

    def _chat_model_name(self) -> str:
        return (
            getattr(self.provider, "chat_model", None)
            or getattr(self.provider, "model", None)
            or "unknown"
        )

    def _history_fingerprint(self, history: list[Message]) -> str:
        payload = [
            {"role": message.role, "content": message.content}
            for message in history
        ]
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
