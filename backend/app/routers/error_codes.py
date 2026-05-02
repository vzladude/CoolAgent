"""
Error-code endpoints by manufacturer and model.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.error_code import ErrorCode, Manufacturer
from app.schemas.error_codes import ErrorCodeResponse, ManufacturerResponse

router = APIRouter()


@router.get("/", response_model=list[ErrorCodeResponse])
async def search_error_codes(
    query: str | None = Query(None, description="Buscar en codigo, descripcion, fabricante o modelo"),
    code: str | None = Query(None, description="Codigo de error a buscar"),
    manufacturer: str | None = Query(None, description="Filtrar por fabricante"),
    model: str | None = Query(None, description="Filtrar por modelo"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Search error codes with optional manufacturer/model filters."""
    filters = []
    if query:
        pattern = f"%{query.strip()}%"
        filters.append(
            or_(
                ErrorCode.code.ilike(pattern),
                ErrorCode.description.ilike(pattern),
                ErrorCode.manufacturer.ilike(pattern),
                ErrorCode.model.ilike(pattern),
            )
        )
    if code:
        filters.append(ErrorCode.code.ilike(f"%{code.strip()}%"))
    if manufacturer:
        filters.append(ErrorCode.manufacturer.ilike(f"%{manufacturer.strip()}%"))
    if model:
        filters.append(ErrorCode.model.ilike(f"%{model.strip()}%"))

    result = await db.execute(
        select(ErrorCode)
        .where(*filters)
        .order_by(
            ErrorCode.manufacturer.asc(),
            ErrorCode.model.asc().nullslast(),
            ErrorCode.code.asc(),
        )
        .limit(limit)
        .offset(offset)
    )
    return [_error_code_response(error_code) for error_code in result.scalars().all()]


@router.get("/manufacturers", response_model=list[ManufacturerResponse])
async def list_manufacturers(
    db: AsyncSession = Depends(get_db),
):
    """List manufacturers with real model and error-code counts."""
    result = await db.execute(
        select(
            Manufacturer,
            func.count(ErrorCode.id).label("error_code_count"),
            func.count(distinct(ErrorCode.model)).label("model_count"),
        )
        .outerjoin(ErrorCode, ErrorCode.manufacturer_id == Manufacturer.id)
        .group_by(Manufacturer.id)
        .order_by(Manufacturer.name.asc())
    )
    return [
        ManufacturerResponse(
            id=manufacturer.id,
            name=manufacturer.name,
            country=manufacturer.country,
            website=manufacturer.website,
            model_count=model_count,
            error_code_count=error_code_count,
        )
        for manufacturer, error_code_count, model_count in result.all()
    ]


def _error_code_response(error_code: ErrorCode) -> ErrorCodeResponse:
    return ErrorCodeResponse(
        id=error_code.id,
        code=error_code.code,
        description=error_code.description,
        manufacturer=error_code.manufacturer,
        model=error_code.model,
        severity=error_code.severity,
        possible_causes=error_code.possible_causes or [],
        suggested_fix=error_code.suggested_fix,
        source=error_code.source,
        created_at=error_code.created_at,
        updated_at=error_code.updated_at,
    )
