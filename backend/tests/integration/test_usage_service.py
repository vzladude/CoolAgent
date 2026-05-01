import pytest

from app.services.usage_service import UsageService


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_usage_service_records_tokens_cache_and_blocks(db_session):
    service = UsageService(db_session)

    await service.record_chat_event(
        conversation_id=None,
        message_id=None,
        provider="claude",
        model="fake-claude",
        prompt_policy_version="v1",
        cache_status="miss",
        tokens_input=10,
        tokens_output=5,
    )
    await service.record_chat_event(
        conversation_id=None,
        message_id=None,
        provider="claude",
        model="fake-claude",
        prompt_policy_version="v1",
        cache_status="hit",
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

    assert summary.total_events == 3
    assert summary.provider_requests == 1
    assert summary.cache_misses == 1
    assert summary.cache_hits == 1
    assert summary.domain_blocks == 1
    assert summary.tokens_input == 10
    assert summary.tokens_output == 5
    assert summary.tokens_total == 15
