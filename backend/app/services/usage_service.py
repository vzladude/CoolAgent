"""
Usage monitoring for chat calls.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
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
        message_id: UUID | None,
        provider: str | None,
        model: str | None,
        prompt_policy_version: str | None,
        cache_status: str,
        technical_case_id: UUID | None = None,
        conversation_id: UUID | None = None,
        event_type: str = "chat",
        tokens_input: int = 0,
        tokens_output: int = 0,
        cache_saved_tokens_input: int = 0,
        cache_saved_tokens_output: int = 0,
    ) -> UsageEvent:
        resolved_case_id = technical_case_id or conversation_id
        estimated_cost = self.estimate_cost(
            provider=provider,
            model=model,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )
        estimated_savings = self.estimate_cost(
            provider=provider,
            model=model,
            tokens_input=cache_saved_tokens_input,
            tokens_output=cache_saved_tokens_output,
        )
        event = UsageEvent(
            technical_case_id=resolved_case_id,
            message_id=message_id,
            event_type=event_type,
            provider=provider,
            model=model,
            prompt_policy_version=prompt_policy_version,
            cache_status=cache_status,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_input + tokens_output,
            estimated_cost_usd=estimated_cost,
            cache_saved_tokens_input=cache_saved_tokens_input,
            cache_saved_tokens_output=cache_saved_tokens_output,
            cache_saved_tokens_total=(
                cache_saved_tokens_input + cache_saved_tokens_output
            ),
            cache_saved_cost_usd=estimated_savings,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_summary(
        self,
        technical_case_id: UUID | None = None,
        conversation_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        model: str | None = None,
    ) -> UsageSummaryResponse:
        filters = self._build_filters(
            technical_case_id=technical_case_id or conversation_id,
            date_from=date_from,
            date_to=date_to,
            model=model,
        )

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
                func.coalesce(func.sum(UsageEvent.estimated_cost_usd), 0),
                func.count(UsageEvent.estimated_cost_usd),
                func.coalesce(func.sum(UsageEvent.cache_saved_tokens_input), 0),
                func.coalesce(func.sum(UsageEvent.cache_saved_tokens_output), 0),
                func.coalesce(func.sum(UsageEvent.cache_saved_tokens_total), 0),
                func.coalesce(func.sum(UsageEvent.cache_saved_cost_usd), 0),
                func.count(UsageEvent.cache_saved_cost_usd),
            ).where(*filters)
        )
        (
            total_events,
            tokens_input,
            tokens_output,
            tokens_total,
            estimated_cost,
            estimated_cost_count,
            saved_tokens_input,
            saved_tokens_output,
            saved_tokens_total,
            estimated_savings,
            estimated_savings_count,
        ) = totals_result.one()

        pricing_configured = (
            self.pricing_configured(provider=None, model=model)
            or estimated_cost_count > 0
            or estimated_savings_count > 0
        )

        return UsageSummaryResponse(
            pricing_configured=pricing_configured,
            total_events=total_events,
            provider_requests=counts.get("miss", 0),
            cache_hits=counts.get("hit", 0),
            cache_misses=counts.get("miss", 0),
            domain_blocks=counts.get("blocked", 0),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            estimated_cost_usd=self._decimal_to_float_or_none(
                estimated_cost,
                pricing_configured,
            ),
            cache_saved_tokens_input=saved_tokens_input,
            cache_saved_tokens_output=saved_tokens_output,
            cache_saved_tokens_total=saved_tokens_total,
            estimated_cache_savings_usd=self._decimal_to_float_or_none(
                estimated_savings,
                pricing_configured,
            ),
            technical_case_id=technical_case_id or conversation_id,
            conversation_id=technical_case_id or conversation_id,
            date_from=date_from,
            date_to=date_to,
            model=model,
        )

    def estimate_cost(
        self,
        *,
        provider: str | None,
        model: str | None,
        tokens_input: int,
        tokens_output: int,
    ) -> Decimal | None:
        prices = self._token_prices(provider=provider, model=model)
        if prices is None:
            return None
        input_price, output_price = prices
        cost = (
            (Decimal(tokens_input) / Decimal(1_000_000)) * input_price
            + (Decimal(tokens_output) / Decimal(1_000_000)) * output_price
        )
        return cost.quantize(Decimal("0.00000001"))

    def pricing_configured(
        self,
        *,
        provider: str | None,
        model: str | None,
    ) -> bool:
        return self._token_prices(provider=provider, model=model) is not None

    def _build_filters(
        self,
        *,
        technical_case_id: UUID | None,
        date_from: datetime | None,
        date_to: datetime | None,
        model: str | None,
    ) -> list:
        filters = []
        if technical_case_id is not None:
            filters.append(UsageEvent.technical_case_id == technical_case_id)
        if date_from is not None:
            filters.append(UsageEvent.created_at >= date_from)
        if date_to is not None:
            filters.append(UsageEvent.created_at <= date_to)
        if model is not None:
            filters.append(UsageEvent.model == model)
        return filters

    def _token_prices(
        self,
        *,
        provider: str | None,
        model: str | None,
    ) -> tuple[Decimal, Decimal] | None:
        configured = self._configured_price(provider=provider, model=model)
        if configured is not None:
            return configured

        input_price = self.settings.usage_input_cost_per_million_usd
        output_price = self.settings.usage_output_cost_per_million_usd
        if input_price is None or output_price is None:
            return None
        return Decimal(str(input_price)), Decimal(str(output_price))

    def _configured_price(
        self,
        *,
        provider: str | None,
        model: str | None,
    ) -> tuple[Decimal, Decimal] | None:
        if not self.settings.usage_pricing_json:
            return None

        try:
            pricing = json.loads(self.settings.usage_pricing_json)
        except json.JSONDecodeError:
            return None

        lookup_keys = [
            f"{provider}:{model}" if provider and model else None,
            model,
            provider,
            "default",
        ]
        for key in lookup_keys:
            if key and key in pricing:
                return self._parse_price_entry(pricing[key])
        return None

    def _parse_price_entry(self, entry) -> tuple[Decimal, Decimal] | None:
        if not isinstance(entry, dict):
            return None
        input_price = entry.get("input_per_million_usd", entry.get("input"))
        output_price = entry.get("output_per_million_usd", entry.get("output"))
        if input_price is None or output_price is None:
            return None
        return Decimal(str(input_price)), Decimal(str(output_price))

    def _decimal_to_float_or_none(
        self,
        value,
        pricing_configured: bool,
    ) -> float | None:
        if not pricing_configured:
            return None
        return float(value or 0)
