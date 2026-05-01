"""
Usage monitoring for chat calls.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.usage import UsageEvent
from app.schemas.usage import UsageSummaryResponse


class UsageService:
    """Records token usage and summarizes provider/cache activity."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def record_chat_event(
        self,
        *,
        conversation_id: UUID | None,
        message_id: UUID | None,
        provider: str | None,
        model: str | None,
        prompt_policy_version: str | None,
        cache_status: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> UsageEvent:
        event = UsageEvent(
            conversation_id=conversation_id,
            message_id=message_id,
            event_type="chat",
            provider=provider,
            model=model,
            prompt_policy_version=prompt_policy_version,
            cache_status=cache_status,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_input + tokens_output,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_summary(
        self,
        conversation_id: UUID | None = None,
    ) -> UsageSummaryResponse:
        filters = []
        if conversation_id is not None:
            filters.append(UsageEvent.conversation_id == conversation_id)

        counts_result = await self.db.execute(
            select(UsageEvent.cache_status, func.count(UsageEvent.id))
            .where(*filters)
            .group_by(UsageEvent.cache_status)
        )
        counts = {status: count for status, count in counts_result.all()}

        totals_result = await self.db.execute(
            select(
                func.count(UsageEvent.id),
                func.coalesce(func.sum(UsageEvent.tokens_input), 0),
                func.coalesce(func.sum(UsageEvent.tokens_output), 0),
                func.coalesce(func.sum(UsageEvent.tokens_total), 0),
            ).where(*filters)
        )
        total_events, tokens_input, tokens_output, tokens_total = totals_result.one()

        return UsageSummaryResponse(
            total_events=total_events,
            provider_requests=counts.get("miss", 0),
            cache_hits=counts.get("hit", 0),
            cache_misses=counts.get("miss", 0),
            domain_blocks=counts.get("blocked", 0),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            estimated_cost_usd=self._estimate_cost(tokens_input, tokens_output),
            conversation_id=conversation_id,
        )

    def _estimate_cost(self, tokens_input: int, tokens_output: int) -> float | None:
        input_price = self.settings.usage_input_cost_per_million_usd
        output_price = self.settings.usage_output_cost_per_million_usd
        if input_price is None or output_price is None:
            return None
        return round(
            (tokens_input / 1_000_000) * input_price
            + (tokens_output / 1_000_000) * output_price,
            8,
        )
