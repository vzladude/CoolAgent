"""
Schemas de Diagnóstico — Validación de request/response.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DiagnosisResponse(BaseModel):
    id: UUID
    equipment_type: str | None = Field(None, description="Tipo de equipo detectado")
    diagnosis: str = Field(..., description="Diagnóstico principal")
    possible_issues: list[str] = Field(default_factory=list, description="Problemas posibles")
    recommendations: list[str] = Field(default_factory=list, description="Recomendaciones")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza")
    model_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
