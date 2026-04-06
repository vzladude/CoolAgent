"""
Schemas de Códigos de Error.
"""

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

    model_config = {"from_attributes": True}


class ManufacturerResponse(BaseModel):
    name: str
    model_count: int
    error_code_count: int
