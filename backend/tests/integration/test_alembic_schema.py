import pytest
from sqlalchemy import text


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_alembic_creates_pgvector_schema(db_session):
    extension = await db_session.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    )
    assert extension.scalar_one() == "vector"

    embedding_type = await db_session.execute(
        text("""
            SELECT format_type(a.atttypid, a.atttypmod)
              FROM pg_attribute a
              JOIN pg_class c ON c.oid = a.attrelid
              JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'public'
               AND c.relname = 'knowledge_chunks'
               AND a.attname = 'embedding'
               AND NOT a.attisdropped
        """)
    )
    assert embedding_type.scalar_one() == "vector(384)"

    hnsw_index = await db_session.execute(
        text("""
            SELECT indexname
              FROM pg_indexes
             WHERE tablename = 'knowledge_chunks'
               AND indexname = 'ix_knowledge_chunks_embedding_hnsw'
        """)
    )
    assert hnsw_index.scalar_one() == "ix_knowledge_chunks_embedding_hnsw"


@pytest.mark.asyncio
async def test_alembic_creates_usage_tracking_schema(db_session):
    usage_table = await db_session.execute(
        text("""
            SELECT tablename
              FROM pg_tables
             WHERE schemaname = 'public'
               AND tablename = 'usage_events'
        """)
    )
    assert usage_table.scalar_one() == "usage_events"

    cache_index = await db_session.execute(
        text("""
            SELECT indexname
              FROM pg_indexes
             WHERE tablename = 'usage_events'
               AND indexname = 'ix_usage_events_cache_status'
        """)
    )
    assert cache_index.scalar_one() == "ix_usage_events_cache_status"

    cost_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'usage_events'
               AND column_name = 'estimated_cost_usd'
        """)
    )
    assert cost_column.scalar_one() == "estimated_cost_usd"

    model_index = await db_session.execute(
        text("""
            SELECT indexname
              FROM pg_indexes
             WHERE tablename = 'usage_events'
               AND indexname = 'ix_usage_events_model'
        """)
    )
    assert model_index.scalar_one() == "ix_usage_events_model"

    technical_case_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'usage_events'
               AND column_name = 'technical_case_id'
        """)
    )
    assert technical_case_column.scalar_one() == "technical_case_id"


@pytest.mark.asyncio
async def test_alembic_renames_conversations_to_technical_cases(db_session):
    technical_cases = await db_session.execute(
        text("""
            SELECT tablename
              FROM pg_tables
             WHERE schemaname = 'public'
               AND tablename = 'technical_cases'
        """)
    )
    assert technical_cases.scalar_one() == "technical_cases"

    old_conversations = await db_session.execute(
        text("""
            SELECT tablename
              FROM pg_tables
             WHERE schemaname = 'public'
               AND tablename = 'conversations'
        """)
    )
    assert old_conversations.scalar_one_or_none() is None

    message_case_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'messages'
               AND column_name = 'technical_case_id'
        """)
    )
    assert message_case_column.scalar_one() == "technical_case_id"

    summary_column = await db_session.execute(
        text("""
            SELECT column_name
             FROM information_schema.columns
             WHERE table_name = 'technical_cases'
               AND column_name = 'context_summary'
        """)
    )
    assert summary_column.scalar_one() == "context_summary"

    message_fk = await db_session.execute(
        text("""
            SELECT confrelid::regclass::text
              FROM pg_constraint
             WHERE conrelid = 'messages'::regclass
               AND conname = 'fk_messages_technical_case_id_technical_cases'
        """)
    )
    assert message_fk.scalar_one() == "technical_cases"

    status_check = await db_session.execute(
        text("""
            SELECT conname
              FROM pg_constraint
             WHERE conrelid = 'technical_cases'::regclass
               AND conname = 'ck_technical_cases_status'
        """)
    )
    assert status_check.scalar_one() == "ck_technical_cases_status"


@pytest.mark.asyncio
async def test_alembic_prepares_error_code_search_schema(db_session):
    source_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'error_codes'
               AND column_name = 'source'
        """)
    )
    assert source_column.scalar_one() == "source"

    updated_at_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'error_codes'
               AND column_name = 'updated_at'
        """)
    )
    assert updated_at_column.scalar_one() == "updated_at"

    manufacturer_model_index = await db_session.execute(
        text("""
            SELECT indexname
              FROM pg_indexes
             WHERE tablename = 'error_codes'
               AND indexname = 'ix_error_codes_manufacturer_model'
        """)
    )
    assert manufacturer_model_index.scalar_one() == "ix_error_codes_manufacturer_model"

    review_status_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'error_codes'
               AND column_name = 'review_status'
        """)
    )
    assert review_status_column.scalar_one() == "review_status"

    source_document_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'error_codes'
               AND column_name = 'source_document_id'
        """)
    )
    assert source_document_column.scalar_one() == "source_document_id"

    review_status_check = await db_session.execute(
        text("""
            SELECT conname
              FROM pg_constraint
             WHERE conrelid = 'error_codes'::regclass
               AND conname = 'ck_error_codes_review_status'
        """)
    )
    assert review_status_check.scalar_one() == "ck_error_codes_review_status"


@pytest.mark.asyncio
async def test_alembic_creates_users_auth_schema(db_session):
    users_table = await db_session.execute(
        text("""
            SELECT tablename
              FROM pg_tables
             WHERE schemaname = 'public'
               AND tablename = 'users'
        """)
    )
    assert users_table.scalar_one() == "users"

    email_column = await db_session.execute(
        text("""
            SELECT column_name
              FROM information_schema.columns
             WHERE table_name = 'users'
               AND column_name = 'email'
        """)
    )
    assert email_column.scalar_one() == "email"

    unique_email = await db_session.execute(
        text("""
            SELECT conname
              FROM pg_constraint
             WHERE conrelid = 'users'::regclass
               AND conname = 'uq_users_email'
        """)
    )
    assert unique_email.scalar_one() == "uq_users_email"

    email_index = await db_session.execute(
        text("""
            SELECT indexname
              FROM pg_indexes
             WHERE tablename = 'users'
               AND indexname = 'ix_users_email'
        """)
    )
    assert email_index.scalar_one() == "ix_users_email"
