"""
Chat business logic for technical cases.
"""

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts import build_case_prompt
from app.ai.providers import get_ai_provider
from app.ai.providers.base import ChatMessage
from app.config import get_settings
from app.models.technical_case import Message, TechnicalCase
from app.schemas.chat import (
    ChatMessageListResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
    TechnicalCaseCreate,
    TechnicalCaseResponse,
    TechnicalCaseUpdate,
)
from app.services.cache_service import CachedChatResponse, ResponseCache
from app.services.domain_guard import DomainGuard, PROMPT_POLICY_VERSION
from app.services.rag_service import RAGService
from app.services.technical_case_context_service import TechnicalCaseContextService
from app.services.usage_service import UsageService


class ChatService:
    """Service for technical cases and AI chat."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.provider = get_ai_provider()
        self.rag = RAGService(db)
        self.domain_guard = DomainGuard()
        self.cache = ResponseCache()
        self.usage = UsageService(db)
        self.context = TechnicalCaseContextService(db, self.provider, self.usage)

    async def create_case(self, data: TechnicalCaseCreate) -> TechnicalCaseResponse:
        technical_case = TechnicalCase(
            id=uuid4(),
            title=data.title,
            manufacturer=data.manufacturer,
            equipment_model=data.equipment_model,
            category=data.category,
            status=data.status,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(technical_case)
        await self.db.flush()
        return TechnicalCaseResponse.model_validate(technical_case)

    async def create_conversation(
        self, data: ConversationCreate
    ) -> ConversationResponse:
        """Legacy wrapper for /conversations."""
        return await self.create_case(data)

    async def list_cases(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TechnicalCaseResponse]:
        last_message_at = (
            select(func.max(Message.created_at))
            .where(Message.technical_case_id == TechnicalCase.id)
            .correlate(TechnicalCase)
            .scalar_subquery()
        )
        result = await self.db.execute(
            select(TechnicalCase, last_message_at.label("last_message_at"))
            .order_by(TechnicalCase.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [
            TechnicalCaseResponse(
                id=case.id,
                title=case.title,
                manufacturer=case.manufacturer,
                equipment_model=case.equipment_model,
                category=case.category,
                status=case.status,
                created_at=case.created_at,
                updated_at=case.updated_at,
                last_message_at=last_message,
            )
            for case, last_message in result.all()
        ]

    async def get_case(self, technical_case_id: UUID) -> TechnicalCaseResponse:
        technical_case = await self._get_case_or_raise(technical_case_id)
        return TechnicalCaseResponse.model_validate(technical_case)

    async def update_case(
        self,
        technical_case_id: UUID,
        data: TechnicalCaseUpdate,
    ) -> TechnicalCaseResponse:
        technical_case = await self._get_case_or_raise(technical_case_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(technical_case, field, value)
        technical_case.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return TechnicalCaseResponse.model_validate(technical_case)

    async def list_messages(
        self,
        technical_case_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> ChatMessageListResponse:
        await self._get_case_or_raise(technical_case_id)
        total = await self.db.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.technical_case_id == technical_case_id)
        )
        result = await self.db.execute(
            select(Message)
            .where(Message.technical_case_id == technical_case_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        messages = [
            ChatMessageResponse.model_validate(message)
            for message in result.scalars().all()
        ]
        return ChatMessageListResponse(
            messages=messages,
            count=total or 0,
            limit=limit,
            offset=offset,
        )

    async def send_case_message(
        self,
        technical_case_id: UUID,
        data: ChatMessageRequest,
    ) -> ChatMessageResponse:
        technical_case = await self._get_case_or_raise(technical_case_id)

        domain_result = self.domain_guard.evaluate(data.content)
        if not domain_result.is_allowed:
            user_message = self._build_user_message(technical_case_id, data.content)
            assistant_message = self._build_assistant_message(
                technical_case_id=technical_case_id,
                content=domain_result.response or "",
                tokens_used=0,
                model_used=f"domain-guard:{domain_result.policy_version}",
            )
            self.db.add(user_message)
            self.db.add(assistant_message)
            await self.db.flush()
            await self.usage.record_chat_event(
                technical_case_id=technical_case_id,
                message_id=assistant_message.id,
                provider="domain_guard",
                model=assistant_message.model_used,
                prompt_policy_version=domain_result.policy_version,
                cache_status="blocked",
            )
            await self._touch_case_after_user_message(technical_case, data.content)
            await self.db.flush()
            return ChatMessageResponse.model_validate(assistant_message)

        history = await self._get_case_history(technical_case_id)
        case_context = await self.context.prepare_context(technical_case, history)

        user_message = self._build_user_message(technical_case_id, data.content)
        self.db.add(user_message)
        await self._touch_case_after_user_message(technical_case, data.content)

        rag_context = await self.rag.build_context(data.content, limit=3)
        knowledge_fingerprint = await self.rag.knowledge_fingerprint()
        system_prompt = build_case_prompt(case_context.summary, rag_context)

        provider_name = self.settings.ai_provider
        model_name = self._chat_model_name()
        cache_key = self.cache.build_chat_key(
            provider=provider_name,
            model=model_name,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            technical_case_id=str(technical_case_id),
            user_content=data.content,
            rag_context=rag_context,
            context_fingerprint=case_context.context_fingerprint,
            history_fingerprint=self._history_fingerprint(case_context.recent_messages),
            knowledge_fingerprint=knowledge_fingerprint,
        )

        cached_response = await self.cache.get_chat_response(cache_key)
        if cached_response is not None:
            assistant_message = self._build_assistant_message(
                technical_case_id=technical_case_id,
                content=cached_response.content,
                tokens_used=0,
                model_used=f"cache:{cached_response.model}"[:100],
            )
            self.db.add(assistant_message)
            await self.db.flush()
            await self.usage.record_chat_event(
                technical_case_id=technical_case_id,
                message_id=assistant_message.id,
                provider=provider_name,
                model=cached_response.model,
                prompt_policy_version=PROMPT_POLICY_VERSION,
                cache_status="hit",
                cache_saved_tokens_input=cached_response.tokens_input,
                cache_saved_tokens_output=cached_response.tokens_output,
            )
            await self.db.flush()
            return ChatMessageResponse.model_validate(assistant_message)

        ai_messages = self._build_ai_messages(
            system_prompt=system_prompt,
            history=case_context.recent_messages,
            user_content=data.content,
        )
        response = await self.provider.chat(ai_messages)
        tokens_used = response.tokens_input + response.tokens_output

        assistant_message = self._build_assistant_message(
            technical_case_id=technical_case_id,
            content=response.content,
            tokens_used=tokens_used,
            model_used=response.model,
        )
        self.db.add(assistant_message)
        await self.db.flush()

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
            technical_case_id=technical_case_id,
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

    async def send_message(
        self,
        conversation_id: UUID,
        data: ChatMessageRequest,
    ) -> ChatMessageResponse:
        """Legacy wrapper for /conversations/{id}/messages."""
        return await self.send_case_message(conversation_id, data)

    async def stream_case_message(
        self,
        technical_case_id: UUID,
        data: ChatMessageRequest,
    ):
        technical_case = await self._get_case_or_raise(technical_case_id)

        domain_result = self.domain_guard.evaluate(data.content)
        if not domain_result.is_allowed:
            user_message = self._build_user_message(technical_case_id, data.content)
            assistant_message = self._build_assistant_message(
                technical_case_id=technical_case_id,
                content=domain_result.response or "",
                tokens_used=0,
                model_used=f"domain-guard:{domain_result.policy_version}",
            )
            self.db.add(user_message)
            self.db.add(assistant_message)
            await self.db.flush()
            await self.usage.record_chat_event(
                technical_case_id=technical_case_id,
                message_id=assistant_message.id,
                provider="domain_guard",
                model=assistant_message.model_used,
                prompt_policy_version=domain_result.policy_version,
                cache_status="blocked",
            )
            await self._touch_case_after_user_message(technical_case, data.content)
            await self.db.flush()
            yield {"type": "delta", "content": assistant_message.content}
            yield self._done_event(assistant_message, cache_status="blocked")
            return

        history = await self._get_case_history(technical_case_id)
        case_context = await self.context.prepare_context(technical_case, history)

        user_message = self._build_user_message(technical_case_id, data.content)
        self.db.add(user_message)
        await self._touch_case_after_user_message(technical_case, data.content)

        rag_context = await self.rag.build_context(data.content, limit=3)
        knowledge_fingerprint = await self.rag.knowledge_fingerprint()
        system_prompt = build_case_prompt(case_context.summary, rag_context)

        provider_name = self.settings.ai_provider
        model_name = self._chat_model_name()
        cache_key = self.cache.build_chat_key(
            provider=provider_name,
            model=model_name,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            technical_case_id=str(technical_case_id),
            user_content=data.content,
            rag_context=rag_context,
            context_fingerprint=case_context.context_fingerprint,
            history_fingerprint=self._history_fingerprint(case_context.recent_messages),
            knowledge_fingerprint=knowledge_fingerprint,
        )

        cached_response = await self.cache.get_chat_response(cache_key)
        if cached_response is not None:
            assistant_message = self._build_assistant_message(
                technical_case_id=technical_case_id,
                content=cached_response.content,
                tokens_used=0,
                model_used=f"cache:{cached_response.model}"[:100],
            )
            self.db.add(assistant_message)
            await self.db.flush()
            await self.usage.record_chat_event(
                technical_case_id=technical_case_id,
                message_id=assistant_message.id,
                provider=provider_name,
                model=cached_response.model,
                prompt_policy_version=PROMPT_POLICY_VERSION,
                cache_status="hit",
                cache_saved_tokens_input=cached_response.tokens_input,
                cache_saved_tokens_output=cached_response.tokens_output,
            )
            await self.db.flush()
            yield {"type": "delta", "content": assistant_message.content}
            yield self._done_event(assistant_message, cache_status="hit")
            return

        ai_messages = self._build_ai_messages(
            system_prompt=system_prompt,
            history=case_context.recent_messages,
            user_content=data.content,
        )
        content_parts: list[str] = []
        response_model = model_name
        tokens_input = 0
        tokens_output = 0
        finish_reason = None

        async for stream_event in self.provider.chat_stream(ai_messages):
            if stream_event.type == "delta":
                content_parts.append(stream_event.content)
                yield {"type": "delta", "content": stream_event.content}
            elif stream_event.type == "done":
                response_model = stream_event.model or response_model
                tokens_input = stream_event.tokens_input
                tokens_output = stream_event.tokens_output
                finish_reason = stream_event.finish_reason

        full_content = "".join(content_parts)
        tokens_used = tokens_input + tokens_output
        assistant_message = self._build_assistant_message(
            technical_case_id=technical_case_id,
            content=full_content,
            tokens_used=tokens_used,
            model_used=response_model,
        )
        self.db.add(assistant_message)
        await self.db.flush()

        await self.cache.set_chat_response(
            cache_key,
            CachedChatResponse(
                content=full_content,
                model=response_model,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
            ),
        )
        await self.usage.record_chat_event(
            technical_case_id=technical_case_id,
            message_id=assistant_message.id,
            provider=provider_name,
            model=response_model,
            prompt_policy_version=PROMPT_POLICY_VERSION,
            cache_status="miss",
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )
        await self.db.flush()

        done_event = self._done_event(assistant_message, cache_status="miss")
        done_event["finish_reason"] = finish_reason
        yield done_event

    async def stream_message(
        self,
        conversation_id: UUID,
        data: ChatMessageRequest,
    ):
        """Legacy wrapper for /conversations/{id}/messages/stream."""
        async for event in self.stream_case_message(conversation_id, data):
            yield event

    async def _get_case_or_raise(self, technical_case_id: UUID) -> TechnicalCase:
        technical_case = await self.db.get(TechnicalCase, technical_case_id)
        if not technical_case:
            raise ValueError(f"Caso tecnico {technical_case_id} no encontrado")
        return technical_case

    async def _get_case_history(
        self,
        technical_case_id: UUID,
    ) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.technical_case_id == technical_case_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def _get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 20,
    ) -> list[Message]:
        """Legacy helper kept for older unit tests."""
        history = await self._get_case_history(conversation_id)
        return history[-limit:]

    def _build_user_message(self, technical_case_id: UUID, content: str) -> Message:
        return Message(
            id=uuid4(),
            technical_case_id=technical_case_id,
            role="user",
            content=content,
            created_at=datetime.now(timezone.utc),
        )

    def _build_assistant_message(
        self,
        *,
        technical_case_id: UUID,
        content: str,
        tokens_used: int,
        model_used: str,
    ) -> Message:
        return Message(
            id=uuid4(),
            technical_case_id=technical_case_id,
            role="assistant",
            content=content,
            tokens_used=tokens_used,
            model_used=model_used,
            created_at=datetime.now(timezone.utc),
        )

    async def _touch_case_after_user_message(
        self,
        technical_case: TechnicalCase,
        content: str,
    ) -> None:
        if not technical_case.title:
            technical_case.title = self._title_from_first_message(content)
        technical_case.updated_at = datetime.now(timezone.utc)

    def _title_from_first_message(self, content: str) -> str:
        title = " ".join(content.split())[:80].strip()
        return title or "Nuevo caso tecnico"

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

    def _build_ai_messages(
        self,
        *,
        system_prompt: str,
        history: list[Message],
        user_content: str,
    ) -> list[ChatMessage]:
        return [
            ChatMessage(role="system", content=system_prompt),
            *[ChatMessage(role=msg.role, content=msg.content) for msg in history],
            ChatMessage(role="user", content=user_content),
        ]

    def _done_event(self, message: Message, cache_status: str) -> dict:
        return {
            "type": "done",
            "message_id": str(message.id),
            "technical_case_id": str(message.technical_case_id),
            "conversation_id": str(message.technical_case_id),
            "model_used": message.model_used,
            "tokens_used": message.tokens_used or 0,
            "cache_status": cache_status,
            "created_at": message.created_at.isoformat(),
        }
