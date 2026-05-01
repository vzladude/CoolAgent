"""
Schemas de Knowledge Base.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeGlossaryItem(BaseModel):
    """Entrada del glosario vivo de documentos que alimentan el RAG."""

    id: UUID
    title: str
    source: str | None = None
    doc_type: str
    manufacturer: str | None = None
    equipment_model: str | None = None
    category: str | None = None
    chunk_count: int
    metadata: dict | None = None
    created_at: datetime


class KnowledgeGlossaryResponse(BaseModel):
    """Respuesta del glosario RAG."""

    documents: list[KnowledgeGlossaryItem] = Field(default_factory=list)
    count: int
