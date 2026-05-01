"""
Configuración de la base de datos con SQLAlchemy async.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency para inyectar sesión de DB en endpoints."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def ensure_development_schema(conn) -> None:
    """
    Ajustes idempotentes para bases locales ya existentes.

    create_all() crea tablas nuevas, pero no agrega columnas ni cambia tipos cuando
    una tabla ya existe. En produccion esto debe manejarse con Alembic.
    """
    await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))

    await conn.execute(text("""
        ALTER TABLE knowledge_documents
            ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(200),
            ADD COLUMN IF NOT EXISTS equipment_model VARCHAR(200),
            ADD COLUMN IF NOT EXISTS category VARCHAR(100)
    """))
    await conn.execute(text("""
        ALTER TABLE knowledge_chunks
            ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(200),
            ADD COLUMN IF NOT EXISTS equipment_model VARCHAR(200),
            ADD COLUMN IF NOT EXISTS category VARCHAR(100)
    """))

    await conn.execute(text("""
        DO $$
        DECLARE
            embedding_type text;
            chunk_count bigint;
        BEGIN
            SELECT format_type(a.atttypid, a.atttypmod)
              INTO embedding_type
              FROM pg_attribute a
              JOIN pg_class c ON c.oid = a.attrelid
              JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'public'
               AND c.relname = 'knowledge_chunks'
               AND a.attname = 'embedding'
               AND NOT a.attisdropped;

            IF embedding_type IS NOT NULL AND embedding_type <> 'vector(384)' THEN
                SELECT count(*) INTO chunk_count FROM knowledge_chunks;
                IF chunk_count = 0 THEN
                    ALTER TABLE knowledge_chunks
                    ALTER COLUMN embedding TYPE vector(384);
                ELSE
                    RAISE NOTICE 'knowledge_chunks.embedding is %, expected vector(384); skipping automatic migration because chunks exist', embedding_type;
                END IF;
            END IF;
        END $$;
    """))

    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_documents_manufacturer
        ON knowledge_documents (manufacturer)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_documents_equipment_model
        ON knowledge_documents (equipment_model)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_documents_category
        ON knowledge_documents (category)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_manufacturer
        ON knowledge_chunks (manufacturer)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_equipment_model
        ON knowledge_chunks (equipment_model)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_knowledge_chunks_category
        ON knowledge_chunks (category)
    """))
    await conn.execute(text("""
        ALTER TABLE usage_events
            ADD COLUMN IF NOT EXISTS estimated_cost_usd NUMERIC(12, 8),
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_input INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_output INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_total INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_cost_usd NUMERIC(12, 8)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_usage_events_model
        ON usage_events (model)
    """))
