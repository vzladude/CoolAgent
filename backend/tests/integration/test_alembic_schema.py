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
