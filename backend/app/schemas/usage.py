"""
Schemas for usage and cache monitoring.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    pricing_configured: bool
    total_events: int
    provider_requests: int
    cache_hits: int
    cache_misses: int
    domain_blocks: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    estimated_cost_usd: float | None = None
    cache_saved_tokens_input: int
    cache_saved_tokens_output: int
    cache_saved_tokens_total: int
    estimated_cache_savings_usd: float | None = None
    conversation_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    model: str | None = None
