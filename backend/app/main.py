"""
CoolAgent API — Punto de entrada principal.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.database import engine, Base, ensure_development_schema
from app.routers import chat, diagnosis, error_codes, health, knowledge, usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza de recursos."""
    settings = get_settings()

    # Crear tablas en la base de datos (en dev; en prod usar Alembic)
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector"'))
            await conn.run_sync(Base.metadata.create_all)
            await ensure_development_schema(conn)

    print(f"🚀 CoolAgent API iniciada [{settings.environment}]")
    print(f"🤖 AI Provider: {settings.ai_provider}")

    yield

    # Limpieza
    await engine.dispose()
    print("👋 CoolAgent API detenida")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="API backend para CoolAgent — Asistente AI para técnicos HVAC/R",
        lifespan=lifespan,
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.environment == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(
        chat.router,
        prefix=f"{settings.api_v1_prefix}/chat",
        tags=["Chat"],
    )
    app.include_router(
        diagnosis.router,
        prefix=f"{settings.api_v1_prefix}/diagnosis",
        tags=["Diagnosis"],
    )
    app.include_router(
        error_codes.router,
        prefix=f"{settings.api_v1_prefix}/error-codes",
        tags=["Error Codes"],
    )
    app.include_router(
        knowledge.router,
        prefix=f"{settings.api_v1_prefix}/knowledge",
        tags=["Knowledge Base"],
    )
    app.include_router(
        usage.router,
        prefix=f"{settings.api_v1_prefix}/usage",
        tags=["Usage"],
    )

    return app


app = create_app()
