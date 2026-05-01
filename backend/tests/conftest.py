from __future__ import annotations

import os
from pathlib import Path

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEST_DATABASE_URL = (
    "postgresql+asyncpg://coolagent:coolagent_dev@localhost:5432/coolagent_test"
)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: requires a PostgreSQL database with pgvector available",
    )


def get_test_database_url() -> str:
    return os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


def quote_identifier(identifier: str) -> str:
    if not identifier.replace("_", "").isalnum():
        raise ValueError(f"Unsafe database identifier: {identifier}")
    return f'"{identifier}"'


async def recreate_database(database_url: str) -> None:
    url = make_url(database_url)
    database_name = url.database
    if not database_name:
        raise ValueError("TEST_DATABASE_URL must include a database name")

    maintenance_db = os.getenv("TEST_DATABASE_MAINTENANCE_DB", "postgres")
    quoted_name = quote_identifier(database_name)
    conn = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port or 5432,
        database=maintenance_db,
    )
    try:
        await conn.execute(f"DROP DATABASE IF EXISTS {quoted_name} WITH (FORCE)")
        await conn.execute(f"CREATE DATABASE {quoted_name}")
    finally:
        await conn.close()


def run_alembic_upgrade(database_url: str) -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    try:
        command.upgrade(config, "head")
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url


@pytest.fixture(scope="session")
def migrated_test_database_url():
    database_url = get_test_database_url()
    try:
        import asyncio

        asyncio.run(recreate_database(database_url))
        run_alembic_upgrade(database_url)
    except Exception as exc:
        pytest.skip(f"PostgreSQL/pgvector integration database unavailable: {exc}")
    return database_url


@pytest.fixture
async def db_session(migrated_test_database_url):
    engine = create_async_engine(migrated_test_database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.execute(text("""
            TRUNCATE
                usage_events,
                knowledge_chunks,
                knowledge_documents,
                messages,
                conversations,
                error_codes,
                manufacturers
            RESTART IDENTITY CASCADE
        """))

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()
