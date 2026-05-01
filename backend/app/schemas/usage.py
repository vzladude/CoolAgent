"""
Schemas for usage and cache monitoring.
"""

from uuid import UUID

from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    total_events: int
    provider_requests: int
    cache_hits: int
    cache_misses: int
    domain_blocks: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    estimated_cost_usd: float | None = None
    conversation_id: UUID | None = None
