"""
Context management and compaction for technical cases.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import ChatMessage
from app.config import get_settings
from app.models.technical_case import Message, TechnicalCase
from app.services.usage_service import UsageService


MAX_UNSUMMARIZED_MESSAGES = 30
MAX_UNSUMMARIZED_TOKENS = 16_000
RECENT_MESSAGES_TO_KEEP = 10
SUMMARY_MAX_TOKENS = 1_500


@dataclass(frozen=True)
class TechnicalCaseContext:
    summary: str | None
    recent_messages: list[Message]
    context_fingerprint: str


class TechnicalCaseContextService:
    """Builds compact context for a technical case without losing key details."""

    def __init__(
        self,
        db: AsyncSession,
        provider,
        usage: UsageService,
    ):
        self.db = db
        self.provider = provider
        self.usage = usage
        self.settings = get_settings()

    async def prepare_context(
        self,
        technical_case: TechnicalCase,
        history: list[Message],
    ) -> TechnicalCaseContext:
        unsummarized = self._unsummarized_messages(technical_case, history)
        if self._should_compact(unsummarized):
            try:
                await self._compact(technical_case, unsummarized)
            except Exception:
                recent = unsummarized[-RECENT_MESSAGES_TO_KEEP:]
                return self._build_context(technical_case.context_summary, recent)

            unsummarized = self._unsummarized_messages(technical_case, history)

        recent_messages = (
            unsummarized[-RECENT_MESSAGES_TO_KEEP:]
            if technical_case.context_summary
            else unsummarized
        )
        return self._build_context(technical_case.context_summary, recent_messages)

    def estimate_tokens(self, text: str) -> int:
        return math.ceil(len(text) / 4)

    def _unsummarized_messages(
        self,
        technical_case: TechnicalCase,
        history: list[Message],
    ) -> list[Message]:
        if not technical_case.summary_until_message_id:
            return history

        for index, message in enumerate(history):
            if message.id == technical_case.summary_until_message_id:
                return history[index + 1:]
        return history

    def _should_compact(self, messages: list[Message]) -> bool:
        if len(messages) > MAX_UNSUMMARIZED_MESSAGES:
            return True
        estimated_tokens = sum(self.estimate_tokens(message.content) for message in messages)
        return estimated_tokens > MAX_UNSUMMARIZED_TOKENS

    async def _compact(
        self,
        technical_case: TechnicalCase,
        unsummarized: list[Message],
    ) -> None:
        if len(unsummarized) <= RECENT_MESSAGES_TO_KEEP:
            return

        messages_to_summarize = unsummarized[:-RECENT_MESSAGES_TO_KEEP]
        if not messages_to_summarize:
            return

        response = await self.provider.chat(
            self._summary_messages(technical_case, messages_to_summarize),
            temperature=0.2,
            max_tokens=SUMMARY_MAX_TOKENS,
        )

        technical_case.context_summary = response.content
        technical_case.summary_until_message_id = messages_to_summarize[-1].id
        technical_case.summary_updated_at = datetime.now(timezone.utc)
        technical_case.summary_model = response.model
        await self.usage.record_chat_event(
            technical_case_id=technical_case.id,
            message_id=messages_to_summarize[-1].id,
            provider=self.settings.ai_provider,
            model=response.model,
            prompt_policy_version=None,
            cache_status="miss",
            event_type="context_compaction",
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
        )
        await self.db.flush()

    def _summary_messages(
        self,
        technical_case: TechnicalCase,
        messages: list[Message],
    ) -> list[ChatMessage]:
        previous_summary = technical_case.context_summary or "Sin resumen previo."
        metadata = {
            "title": technical_case.title,
            "manufacturer": technical_case.manufacturer,
            "equipment_model": technical_case.equipment_model,
            "category": technical_case.category,
            "status": technical_case.status,
        }
        transcript = "\n".join(
            f"{message.role}: {message.content}" for message in messages
        )
        return [
            ChatMessage(
                role="system",
                content=(
                    "Eres CoolAgent y debes compactar una conversacion tecnica "
                    "de refrigeracion general. Escribe un resumen tecnico en "
                    "espanol, claro y compacto. Conserva equipo/fabricante/modelo, "
                    "sintomas, mediciones, acciones realizadas, diagnosticos "
                    "descartados, riesgos de seguridad, preguntas pendientes y "
                    "fuentes/manuales usados. No inventes datos."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    f"Metadata del caso:\n{json.dumps(metadata, ensure_ascii=False)}\n\n"
                    f"Resumen previo:\n{previous_summary}\n\n"
                    f"Mensajes nuevos a compactar:\n{transcript}"
                ),
            ),
        ]

    def _build_context(
        self,
        summary: str | None,
        recent_messages: list[Message],
    ) -> TechnicalCaseContext:
        payload = {
            "summary": summary or "",
            "recent": [
                {"role": message.role, "content": message.content}
                for message in recent_messages
            ],
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return TechnicalCaseContext(
            summary=summary,
            recent_messages=recent_messages,
            context_fingerprint=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        )
