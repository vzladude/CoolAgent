from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import pytest

from app.ai.providers.base import EmbeddingResponse
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.services import rag_service as rag_module


@dataclass
class FakePage:
    text: str | None

    def extract_text(self):
        return self.text


class FakePdfReader:
    def __init__(self, _file):
        self.pages = [FakePage(None), FakePage("")]


class FakeEmbeddingProvider:
    async def embed(self, text: str) -> EmbeddingResponse:
        return EmbeddingResponse(
            embedding=[1.0] + [0.0] * 383,
            model="fake-embedding",
            dimensions=384,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        return [
            EmbeddingResponse(
                embedding=[1.0] + [0.0] * 383,
                model="fake-embedding",
                dimensions=384,
            )
            for _ in texts
        ]


class FakeDb:
    def __init__(self):
        self.added = []
        self.flush_count = 0

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_count += 1


@pytest.mark.asyncio
async def test_ingest_text_creates_document_chunks_and_metadata(monkeypatch):
    monkeypatch.setattr(
        rag_module,
        "get_embedding_provider",
        lambda: FakeEmbeddingProvider(),
    )
    db = FakeDb()
    service = rag_module.RAGService(db)

    document = await service.ingest_text(
        content="Carrier 38AKS codigo E7 falla del sensor del evaporador.",
        title="Manual Carrier 38AKS",
        source="manual.pdf",
        doc_type="manual",
        manufacturer="Carrier",
        equipment_model="38AKS",
        category="hvac",
    )

    chunks = [obj for obj in db.added if isinstance(obj, KnowledgeChunk)]
    docs = [obj for obj in db.added if isinstance(obj, KnowledgeDocument)]
    assert docs == [document]
    assert document.chunk_count == len(chunks) == 1
    assert document.metadata_["characters"] > 0
    assert chunks[0].manufacturer == "Carrier"
    assert chunks[0].equipment_model == "38AKS"
    assert chunks[0].category == "hvac"
    assert chunks[0].extra_metadata["char_count"] > 0
    assert len(chunks[0].embedding) == 384


@pytest.mark.asyncio
async def test_build_context_formats_sources(monkeypatch):
    monkeypatch.setattr(
        rag_module,
        "get_embedding_provider",
        lambda: FakeEmbeddingProvider(),
    )
    service = rag_module.RAGService(FakeDb())

    async def fake_search(*_args, **_kwargs):
        return [
            {
                "content": "El codigo E7 indica sensor de evaporador.",
                "manufacturer": "Carrier",
                "equipment_model": "38AKS",
                "category": "hvac",
                "document_title": "Manual Carrier",
                "document_source": "manual.pdf",
                "similarity": 0.91,
            }
        ]

    monkeypatch.setattr(service, "search", fake_search)

    context = await service.build_context("Que es E7?")

    assert context is not None
    assert "El codigo E7" in context
    assert "Fuente: Manual Carrier" in context
    assert "Carrier 38AKS" in context


@pytest.mark.asyncio
async def test_ingest_pdf_without_extractable_text_fails(monkeypatch):
    monkeypatch.setattr(
        rag_module,
        "get_embedding_provider",
        lambda: FakeEmbeddingProvider(),
    )
    monkeypatch.setattr(rag_module, "PdfReader", FakePdfReader)
    service = rag_module.RAGService(FakeDb())

    with pytest.raises(ValueError, match="No se pudo extraer texto"):
        await service.ingest_pdf(
            file=BytesIO(b"not-a-real-pdf"),
            title="PDF vacio",
        )
