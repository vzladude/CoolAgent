"""
Usage monitoring endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.usage import UsageSummaryResponse
from app.services.usage_service import UsageService

router = APIRouter()


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    conversation_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return token and cache activity summary."""
    service = UsageService(db)
    return await service.get_summary(conversation_id=conversation_id)
