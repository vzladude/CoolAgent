"""
Usage monitoring endpoints.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.usage import UsageSummaryResponse
from app.services.usage_service import UsageService

router = APIRouter()


@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
    technical_case_id: UUID | None = Query(None),
    conversation_id: UUID | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    model: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return token and cache activity summary."""
    service = UsageService(db)
    return await service.get_summary(
        technical_case_id=technical_case_id,
        conversation_id=conversation_id,
        date_from=date_from,
        date_to=date_to,
        model=model,
    )
