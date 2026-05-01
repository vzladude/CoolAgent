import pytest

from app.services.usage_service import UsageService


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_usage_service_records_tokens_cache_and_blocks(db_session):
    service = UsageService(db_session)
    original_input_price = service.settings.usage_input_cost_per_million_usd
    original_output_price = service.settings.usage_output_cost_per_million_usd
    original_pricing_json = service.settings.usage_pricing_json
    service.settings.usage_input_cost_per_million_usd = 2.0
    service.settings.usage_output_cost_per_million_usd = 6.0
    service.settings.usage_pricing_json = ""

    try:
        await service.record_chat_event(
            conversation_id=None,
            message_id=None,
            provider="claude",
            model="fake-claude",
            prompt_policy_version="v1",
            cache_status="miss",
            tokens_input=1_000_000,
            tokens_output=500_000,
        )
        await service.record_chat_event(
            conversation_id=None,
            message_id=None,
            provider="claude",
            model="fake-claude",
            prompt_policy_version="v1",
            cache_status="hit",
            cache_saved_tokens_input=1_000_000,
            cache_saved_tokens_output=500_000,
        )
        await service.record_chat_event(
            conversation_id=None,
            message_id=None,
            provider="domain_guard",
            model="domain-guard:v1",
            prompt_policy_version="v1",
            cache_status="blocked",
        )

        summary = await service.get_summary()

        assert summary.pricing_configured is True
        assert summary.total_events == 3
        assert summary.provider_requests == 1
        assert summary.cache_misses == 1
        assert summary.cache_hits == 1
        assert summary.domain_blocks == 1
        assert summary.tokens_input == 1_000_000
        assert summary.tokens_output == 500_000
        assert summary.tokens_total == 1_500_000
        assert summary.estimated_cost_usd == 5.0
        assert summary.cache_saved_tokens_input == 1_000_000
        assert summary.cache_saved_tokens_output == 500_000
        assert summary.cache_saved_tokens_total == 1_500_000
        assert summary.estimated_cache_savings_usd == 5.0

        model_summary = await service.get_summary(model="fake-claude")
        assert model_summary.total_events == 2
        assert model_summary.domain_blocks == 0
    finally:
        service.settings.usage_input_cost_per_million_usd = original_input_price
        service.settings.usage_output_cost_per_million_usd = original_output_price
        service.settings.usage_pricing_json = original_pricing_json


@pytest.mark.asyncio
async def test_usage_service_supports_model_pricing_json(db_session):
    service = UsageService(db_session)
    original_input_price = service.settings.usage_input_cost_per_million_usd
    original_output_price = service.settings.usage_output_cost_per_million_usd
    original_pricing_json = service.settings.usage_pricing_json
    service.settings.usage_input_cost_per_million_usd = None
    service.settings.usage_output_cost_per_million_usd = None
    service.settings.usage_pricing_json = (
        '{"claude:fake-claude":{"input":3.0,"output":9.0}}'
    )

    try:
        await service.record_chat_event(
            conversation_id=None,
            message_id=None,
            provider="claude",
            model="fake-claude",
            prompt_policy_version="v1",
            cache_status="miss",
            tokens_input=1_000_000,
            tokens_output=1_000_000,
        )

        summary = await service.get_summary(model="fake-claude")

        assert summary.pricing_configured is True
        assert summary.estimated_cost_usd == 12.0
    finally:
        service.settings.usage_input_cost_per_million_usd = original_input_price
        service.settings.usage_output_cost_per_million_usd = original_output_price
        service.settings.usage_pricing_json = original_pricing_json
