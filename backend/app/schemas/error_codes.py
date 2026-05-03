"""
Schemas de Códigos de Error.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorCodeResponse(BaseModel):
    id: UUID
    code: str
    description: str
    manufacturer: str
    model: str | None = None
    severity: str | None = Field(None, description="low | medium | high | critical")
    possible_causes: list[str] = Field(default_factory=list)
    suggested_fix: str | None = None
    source: str | None = None
    source_document_id: UUID | None = None
    source_chunk_id: UUID | None = None
    source_page: int | None = None
    source_excerpt: str | None = None
    review_status: str = "approved"
    confidence: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManufacturerResponse(BaseModel):
    id: UUID
    name: str
    country: str | None = None
    website: str | None = None
    model_count: int
    error_code_count: int


class ErrorCodeExtractionRequest(BaseModel):
    auto_approve: bool = Field(
        False,
        description="Si es true, los codigos extraidos quedan aprobados de inmediato.",
    )
    max_codes: int = Field(
        100,
        ge=1,
        le=500,
        description="Cantidad maxima de candidatos a extraer del documento.",
    )


class ErrorCodeExtractionResponse(BaseModel):
    document_id: UUID
    created: int
    skipped_existing: int
    status: str
    error_codes: list[ErrorCodeResponse] = Field(default_factory=list)


class ErrorCodeReviewRequest(BaseModel):
    review_status: str = Field(
        ...,
        description="Estado de revision: pending_review, approved o rejected.",
    )


class ErrorCodeUpdateRequest(BaseModel):
    code: str | None = Field(None, description="Codigo de error corregido.")
    description: str | None = Field(None, description="Descripcion tecnica corregida.")
    model: str | None = Field(None, description="Modelo asociado al codigo.")
    severity: str | None = Field(
        None,
        description="Severidad: low, medium, high o critical.",
    )
    possible_causes: list[str] | None = Field(
        None,
        description="Causas probables revisadas.",
    )
    suggested_fix: str | None = Field(None, description="Solucion sugerida revisada.")
    source: str | None = Field(None, description="Fuente legible para mostrar.")
    source_page: int | None = Field(
        None,
        ge=1,
        description="Pagina de la fuente donde aparece el codigo.",
    )
    source_excerpt: str | None = Field(
        None,
        description="Fragmento corto de fuente usado para revisar el codigo.",
    )
