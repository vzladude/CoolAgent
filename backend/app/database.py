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
        DO $$
        BEGIN
            IF to_regclass('public.technical_cases') IS NULL
               AND to_regclass('public.conversations') IS NOT NULL THEN
                ALTER TABLE conversations RENAME TO technical_cases;
            END IF;
        END $$;
    """))
    await conn.execute(text("""
        ALTER TABLE technical_cases
            ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(200),
            ADD COLUMN IF NOT EXISTS equipment_model VARCHAR(200),
            ADD COLUMN IF NOT EXISTS category VARCHAR(100),
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'open',
            ADD COLUMN IF NOT EXISTS context_summary TEXT,
            ADD COLUMN IF NOT EXISTS summary_until_message_id UUID,
            ADD COLUMN IF NOT EXISTS summary_updated_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS summary_model VARCHAR(150)
    """))
    await conn.execute(text("""
        DO $$
        DECLARE
            constraint_record record;
        BEGIN
            IF to_regclass('public.conversations') IS NOT NULL THEN
                INSERT INTO technical_cases (
                    id,
                    title,
                    status,
                    created_at,
                    updated_at
                )
                SELECT
                    conversations.id,
                    conversations.title,
                    'open',
                    conversations.created_at,
                    conversations.updated_at
                FROM conversations
                ON CONFLICT (id) DO NOTHING;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE messages
                RENAME COLUMN conversation_id TO technical_case_id;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) THEN
                UPDATE messages
                   SET technical_case_id = conversation_id
                 WHERE technical_case_id IS NULL;
                ALTER TABLE messages DROP COLUMN conversation_id;
            END IF;

            IF to_regclass('public.usage_events') IS NOT NULL
               AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE usage_events
                RENAME COLUMN conversation_id TO technical_case_id;
            END IF;

            IF to_regclass('public.usage_events') IS NOT NULL
               AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) THEN
                UPDATE usage_events
                   SET technical_case_id = conversation_id
                 WHERE technical_case_id IS NULL;
                ALTER TABLE usage_events DROP COLUMN conversation_id;
            END IF;

            FOR constraint_record IN
                SELECT DISTINCT c.conname
                  FROM pg_constraint c
                  JOIN pg_attribute a
                    ON a.attrelid = c.conrelid
                   AND a.attnum = ANY(c.conkey)
                 WHERE c.conrelid = 'public.messages'::regclass
                   AND c.contype = 'f'
                   AND a.attname IN ('conversation_id', 'technical_case_id')
            LOOP
                EXECUTE format(
                    'ALTER TABLE messages DROP CONSTRAINT IF EXISTS %I',
                    constraint_record.conname
                );
            END LOOP;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_messages_technical_case_id_technical_cases'
                   AND conrelid = 'public.messages'::regclass
            ) THEN
                ALTER TABLE messages
                ADD CONSTRAINT fk_messages_technical_case_id_technical_cases
                FOREIGN KEY (technical_case_id)
                REFERENCES technical_cases(id)
                ON DELETE CASCADE;
            END IF;

            IF to_regclass('public.usage_events') IS NOT NULL THEN
                FOR constraint_record IN
                    SELECT DISTINCT c.conname
                      FROM pg_constraint c
                      JOIN pg_attribute a
                        ON a.attrelid = c.conrelid
                       AND a.attnum = ANY(c.conkey)
                     WHERE c.conrelid = 'public.usage_events'::regclass
                       AND c.contype = 'f'
                       AND a.attname IN ('conversation_id', 'technical_case_id')
                LOOP
                    EXECUTE format(
                        'ALTER TABLE usage_events DROP CONSTRAINT IF EXISTS %I',
                        constraint_record.conname
                    );
                END LOOP;

                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                     WHERE conname = 'fk_usage_events_technical_case_id_technical_cases'
                       AND conrelid = 'public.usage_events'::regclass
                ) THEN
                    ALTER TABLE usage_events
                    ADD CONSTRAINT fk_usage_events_technical_case_id_technical_cases
                    FOREIGN KEY (technical_case_id)
                    REFERENCES technical_cases(id)
                    ON DELETE SET NULL;
                END IF;
            END IF;

            IF to_regclass('public.conversations') IS NOT NULL THEN
                DROP TABLE conversations;
            END IF;
        END $$;
    """))
    await conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'ck_technical_cases_status'
                   AND conrelid = 'public.technical_cases'::regclass
            ) THEN
                ALTER TABLE technical_cases
                ADD CONSTRAINT ck_technical_cases_status
                CHECK (status IN ('open', 'closed'));
            END IF;
        END $$;
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_technical_cases_status
        ON technical_cases (status)
    """))
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_messages_technical_case_id
        ON messages (technical_case_id)
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
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_usage_events_technical_case_id
        ON usage_events (technical_case_id)
    """))
