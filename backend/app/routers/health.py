"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check básico."""
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.environment,
        "ai_provider": settings.ai_provider,
    }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Verificar conexión a PostgreSQL."""
    result = await db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected", "result": result.scalar()}
