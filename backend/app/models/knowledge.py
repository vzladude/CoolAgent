"""
Modelos de Knowledge Base — Documentos y chunks para RAG con pgvector.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


class KnowledgeDocument(Base):
    """Documento fuente ingresado en la knowledge base."""
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500))
    source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    doc_type: Mapped[str] = mapped_column(
        String(50), default="general"
    )  # general, manual, datasheet, guide, faq, book
    manufacturer: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    equipment_model: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )  # refrigeration, hvac, electrical, general, etc.
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class KnowledgeChunk(Base):
    """Fragmento de un documento con su embedding para búsqueda semántica."""
    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
    )
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    # Filtros desnormalizados del documento (para queries rápidas sin JOIN)
    manufacturer: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    equipment_model: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    extra_metadata: Mapped[dict | None] = mapped_column("chunk_metadata", JSON, nullable=True)

    # Vector embedding — all-MiniLM-L6-v2 genera 384 dimensiones
    embedding = mapped_column(Vector(384), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación
    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")
