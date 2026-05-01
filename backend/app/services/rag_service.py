"""
Servicio RAG — Retrieval-Augmented Generation.
Pipeline completo: ingesta de documentos → chunking → embeddings → búsqueda semántica.
Soporta filtros opcionales por fabricante, modelo de equipo y categoría.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import BinaryIO

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.local_embedding_provider import get_embedding_provider
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk


class RAGService:
    """Pipeline RAG: ingesta, chunking, embeddings, y búsqueda semántica."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_provider = get_embedding_provider()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    # ─── INGESTA ─────────────────────────────────────────

    async def ingest_pdf(
        self,
        file: BinaryIO,
        title: str,
        source: str | None = None,
        doc_type: str = "general",
        manufacturer: str | None = None,
        equipment_model: str | None = None,
        category: str | None = None,
    ) -> KnowledgeDocument:
        """
        Ingestar un PDF: extraer texto → chunking → embeddings → pgvector.
        Los filtros (manufacturer, equipment_model, category) son opcionales.
        """
        # 1. Extraer texto del PDF
        reader = PdfReader(file)
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n\n"

        if not full_text.strip():
            raise ValueError("No se pudo extraer texto del PDF")

        # 2. Crear documento en DB
        document = KnowledgeDocument(
            id=uuid.uuid4(),
            title=title,
            source=source,
            doc_type=doc_type,
            manufacturer=manufacturer,
            equipment_model=equipment_model,
            category=category,
            metadata_={"pages": len(reader.pages), "characters": len(full_text)},
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(document)
        await self.db.flush()

        # 3. Chunking → Embeddings → Guardar
        await self._process_chunks(document, full_text)

        return document

    async def ingest_text(
        self,
        content: str,
        title: str,
        source: str | None = None,
        doc_type: str = "guide",
        manufacturer: str | None = None,
        equipment_model: str | None = None,
        category: str | None = None,
    ) -> KnowledgeDocument:
        """Ingestar texto plano directamente."""
        document = KnowledgeDocument(
            id=uuid.uuid4(),
            title=title,
            source=source,
            doc_type=doc_type,
            manufacturer=manufacturer,
            equipment_model=equipment_model,
            category=category,
            metadata_={"characters": len(content)},
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(document)
        await self.db.flush()

        await self._process_chunks(document, content)

        return document

    async def _process_chunks(
        self,
        document: KnowledgeDocument,
        full_text: str,
    ) -> None:
        """Chunking → Embeddings → Guardar en pgvector."""
        chunks_text = self.text_splitter.split_text(full_text)
        embedding_responses = await self.embedding_provider.embed_batch(chunks_text)

        for i, (chunk_text, emb_response) in enumerate(
            zip(chunks_text, embedding_responses)
        ):
            chunk = KnowledgeChunk(
                id=uuid.uuid4(),
                document_id=document.id,
                content=chunk_text,
                chunk_index=i,
                # Filtros desnormalizados del documento para búsqueda rápida
                manufacturer=document.manufacturer,
                equipment_model=document.equipment_model,
                category=document.category,
                extra_metadata={"char_count": len(chunk_text)},
                embedding=emb_response.embedding,
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(chunk)

        document.chunk_count = len(chunks_text)
        await self.db.flush()

    # ─── BÚSQUEDA SEMÁNTICA ──────────────────────────────

    async def search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.3,
        manufacturer: str | None = None,
        equipment_model: str | None = None,
        category: str | None = None,
    ) -> list[dict]:
        """
        Buscar los chunks más relevantes para una query.
        Filtros opcionales acotan la búsqueda antes de comparar vectores.
        """
        query_response = await self.embedding_provider.embed(query)
        query_embedding = query_response.embedding

        # Construir query con filtros opcionales
        vector_expr = "CAST(:embedding AS vector)"
        where_clauses = [
            f"1 - (kc.embedding <=> {vector_expr}) > :threshold"
        ]
        params = {
            "embedding": str(query_embedding),
            "threshold": similarity_threshold,
            "limit": limit,
        }

        if manufacturer:
            where_clauses.append("kc.manufacturer ILIKE :manufacturer")
            params["manufacturer"] = f"%{manufacturer}%"

        if equipment_model:
            where_clauses.append("kc.equipment_model ILIKE :equipment_model")
            params["equipment_model"] = f"%{equipment_model}%"

        if category:
            where_clauses.append("kc.category = :category")
            params["category"] = category

        where_sql = " AND ".join(where_clauses)

        result = await self.db.execute(
            text(f"""
                SELECT
                    kc.id,
                    kc.content,
                    kc.manufacturer,
                    kc.equipment_model,
                    kc.category,
                    kd.title as document_title,
                    kd.source as document_source,
                    1 - (kc.embedding <=> {vector_expr}) as similarity
                FROM knowledge_chunks kc
                JOIN knowledge_documents kd ON kd.id = kc.document_id
                WHERE {where_sql}
                ORDER BY kc.embedding <=> {vector_expr}
                LIMIT :limit
            """),
            params,
        )

        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "content": row.content,
                "manufacturer": row.manufacturer,
                "equipment_model": row.equipment_model,
                "category": row.category,
                "document_title": row.document_title,
                "document_source": row.document_source,
                "similarity": round(float(row.similarity), 4),
            }
            for row in rows
        ]

    async def build_context(
        self,
        query: str,
        limit: int = 3,
        manufacturer: str | None = None,
        equipment_model: str | None = None,
        category: str | None = None,
    ) -> str | None:
        """
        Construir contexto RAG para inyectar en el prompt del chat.
        Retorna el texto formateado o None si no hay resultados relevantes.
        """
        results = await self.search(
            query,
            limit=limit,
            manufacturer=manufacturer,
            equipment_model=equipment_model,
            category=category,
        )

        if not results:
            return None

        context_parts = []
        for r in results:
            source_info = f"Fuente: {r['document_title']}"
            if r["manufacturer"]:
                source_info += f" | {r['manufacturer']}"
            if r["equipment_model"]:
                source_info += f" {r['equipment_model']}"
            context_parts.append(f"---\n{r['content']}\n({source_info})\n")

        return "\n".join(context_parts)

    async def knowledge_fingerprint(self) -> str:
        """Return a stable fingerprint for the current knowledge base state."""
        result = await self.db.execute(
            text("""
                SELECT
                    (SELECT COUNT(*) FROM knowledge_documents) AS document_count,
                    (SELECT COALESCE(SUM(chunk_count), 0)
                       FROM knowledge_documents) AS declared_chunk_count,
                    (SELECT COALESCE(MAX(created_at)::text, '')
                       FROM knowledge_documents) AS latest_document_at,
                    (SELECT COUNT(*) FROM knowledge_chunks) AS chunk_count,
                    (SELECT COALESCE(MAX(created_at)::text, '')
                       FROM knowledge_chunks) AS latest_chunk_at
            """)
        )
        row = result.one()
        payload = {
            "document_count": row.document_count,
            "declared_chunk_count": row.declared_chunk_count,
            "latest_document_at": row.latest_document_at,
            "chunk_count": row.chunk_count,
            "latest_chunk_at": row.latest_chunk_at,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ─── ADMINISTRACIÓN ──────────────────────────────────

    async def list_documents(
        self,
        manufacturer: str | None = None,
        category: str | None = None,
    ) -> list[dict]:
        """Listar documentos, opcionalmente filtrados."""
        query = select(KnowledgeDocument).order_by(
            KnowledgeDocument.created_at.desc()
        )

        if manufacturer:
            query = query.where(
                KnowledgeDocument.manufacturer.ilike(f"%{manufacturer}%")
            )
        if category:
            query = query.where(KnowledgeDocument.category == category)

        result = await self.db.execute(query)
        docs = result.scalars().all()
        return [
            {
                "id": str(d.id),
                "title": d.title,
                "source": d.source,
                "doc_type": d.doc_type,
                "manufacturer": d.manufacturer,
                "equipment_model": d.equipment_model,
                "category": d.category,
                "chunk_count": d.chunk_count,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ]

    async def glossary(
        self,
        manufacturer: str | None = None,
        category: str | None = None,
        doc_type: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        """
        Catálogo vivo de documentos que alimentan el RAG.

        Retorna metadata del documento, no contenido completo de chunks.
        """
        query = select(KnowledgeDocument).order_by(
            KnowledgeDocument.created_at.desc()
        )

        if manufacturer:
            query = query.where(
                KnowledgeDocument.manufacturer.ilike(f"%{manufacturer}%")
            )
        if category:
            query = query.where(KnowledgeDocument.category == category)
        if doc_type:
            query = query.where(KnowledgeDocument.doc_type == doc_type)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    KnowledgeDocument.title.ilike(pattern),
                    KnowledgeDocument.source.ilike(pattern),
                )
            )

        result = await self.db.execute(query)
        docs = result.scalars().all()
        return [
            {
                "id": d.id,
                "title": d.title,
                "source": d.source,
                "doc_type": d.doc_type,
                "manufacturer": d.manufacturer,
                "equipment_model": d.equipment_model,
                "category": d.category,
                "chunk_count": d.chunk_count,
                "metadata": d.metadata_,
                "created_at": d.created_at,
            }
            for d in docs
        ]

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """Eliminar un documento y todos sus chunks."""
        doc = await self.db.get(KnowledgeDocument, document_id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.flush()
        return True
