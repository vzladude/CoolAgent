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
