import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.models.user import User
from app.services.auth_service import hash_password
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


@pytest.mark.asyncio
async def test_usage_service_scopes_summary_by_user(db_session):
    now = datetime.now(timezone.utc)
    user_a = User(
        id=uuid4(),
        email="usage-a@example.com",
        password_hash=hash_password("super-secret-123"),
        created_at=now,
        updated_at=now,
    )
    user_b = User(
        id=uuid4(),
        email="usage-b@example.com",
        password_hash=hash_password("super-secret-123"),
        created_at=now,
        updated_at=now,
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    service_a = UsageService(db_session, user_id=user_a.id)
    service_b = UsageService(db_session, user_id=user_b.id)

    await service_a.record_chat_event(
        message_id=None,
        provider="claude",
        model="fake-claude",
        prompt_policy_version="v1",
        cache_status="miss",
        tokens_input=10,
        tokens_output=5,
    )
    await service_b.record_chat_event(
        message_id=None,
        provider="claude",
        model="fake-claude",
        prompt_policy_version="v1",
        cache_status="miss",
        tokens_input=20,
        tokens_output=5,
    )

    summary_a = await service_a.get_summary()
    summary_b = await service_b.get_summary()
    summary_local = await UsageService(db_session).get_summary()

    assert summary_a.total_events == 1
    assert summary_a.tokens_input == 10
    assert summary_a.user_id == user_a.id
    assert summary_b.total_events == 1
    assert summary_b.tokens_input == 20
    assert summary_b.user_id == user_b.id
    assert summary_local.total_events == 2
