"""
Error-code endpoints by manufacturer and model.
"""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import and_, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.error_code import ErrorCode, Manufacturer
from app.schemas.error_codes import (
    ErrorCodeExtractionRequest,
    ErrorCodeExtractionResponse,
    ErrorCodeResponse,
    ErrorCodeReviewRequest,
    ManufacturerResponse,
)
from app.services.error_code_extraction_service import (
    ErrorCodeExtractionService,
    validate_review_status,
)

router = APIRouter()


@router.get("/", response_model=list[ErrorCodeResponse])
async def search_error_codes(
    query: str | None = Query(None, description="Buscar en codigo, descripcion, fabricante o modelo"),
    code: str | None = Query(None, description="Codigo de error a buscar"),
    manufacturer: str | None = Query(None, description="Filtrar por fabricante"),
    model: str | None = Query(None, description="Filtrar por modelo"),
    review_status: str | None = Query(
        "approved",
        description="Filtrar por estado: approved, pending_review, rejected o all",
    ),
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
    requested_review_status = review_status.strip().lower() if review_status else None
    if requested_review_status and requested_review_status != "all":
        try:
            filters.append(
                ErrorCode.review_status == validate_review_status(requested_review_status)
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

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
    review_status: str | None = Query(
        "approved",
        description="Contar codigos por estado: approved, pending_review, rejected o all",
    ),
    db: AsyncSession = Depends(get_db),
):
    """List manufacturers with real model and error-code counts."""
    join_conditions = [ErrorCode.manufacturer_id == Manufacturer.id]
    requested_review_status = review_status.strip().lower() if review_status else None
    if requested_review_status and requested_review_status != "all":
        try:
            join_conditions.append(
                ErrorCode.review_status == validate_review_status(requested_review_status)
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

    result = await db.execute(
        select(
            Manufacturer,
            func.count(ErrorCode.id).label("error_code_count"),
            func.count(distinct(ErrorCode.model)).label("model_count"),
        )
        .outerjoin(ErrorCode, and_(*join_conditions))
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


@router.post(
    "/extract/from-document/{document_id}",
    response_model=ErrorCodeExtractionResponse,
)
async def extract_error_codes_from_document(
    document_id: UUID,
    payload: ErrorCodeExtractionRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract error-code candidates from a knowledge document.

    The source PDF/text remains in Knowledge. Extracted records are a derived
    index and default to pending_review until manually approved.
    """
    request = payload or ErrorCodeExtractionRequest()
    service = ErrorCodeExtractionService(db)
    try:
        created, skipped_existing = await service.extract_from_document(
            document_id,
            auto_approve=request.auto_approve,
            max_codes=request.max_codes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ErrorCodeExtractionResponse(
        document_id=document_id,
        created=len(created),
        skipped_existing=skipped_existing,
        status="approved" if request.auto_approve else "pending_review",
        error_codes=[_error_code_response(error_code) for error_code in created],
    )


@router.patch("/{error_code_id}/review", response_model=ErrorCodeResponse)
async def review_error_code(
    error_code_id: UUID,
    payload: ErrorCodeReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """Approve, reject, or return an extracted code to pending review."""
    try:
        review_status = validate_review_status(payload.review_status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    error_code = await db.get(ErrorCode, error_code_id)
    if error_code is None:
        raise HTTPException(status_code=404, detail="Codigo de error no encontrado")

    error_code.review_status = review_status
    await db.flush()
    return _error_code_response(error_code)


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
        source_document_id=error_code.source_document_id,
        source_chunk_id=error_code.source_chunk_id,
        source_page=error_code.source_page,
        source_excerpt=error_code.source_excerpt,
        review_status=error_code.review_status,
        confidence=error_code.confidence,
        created_at=error_code.created_at,
        updated_at=error_code.updated_at,
    )
