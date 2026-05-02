from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.ai.providers.base import EmbeddingResponse
from app.database import get_db
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.routers.knowledge import router as knowledge_router
from app.services import rag_service as rag_module


pytestmark = pytest.mark.integration


class FakeEmbeddingProvider:
    def vector_for(self, text: str) -> list[float]:
        if "E7" in text or "evaporador" in text:
            return [1.0] + [0.0] * 383
        return [0.0, 1.0] + [0.0] * 382

    async def embed(self, text: str) -> EmbeddingResponse:
        return EmbeddingResponse(
            embedding=self.vector_for(text),
            model="fake-embedding",
            dimensions=384,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        return [
            EmbeddingResponse(
                embedding=self.vector_for(text),
                model="fake-embedding",
                dimensions=384,
            )
            for text in texts
        ]


@pytest.fixture
def fake_embeddings(monkeypatch):
    monkeypatch.setattr(
        rag_module,
        "get_embedding_provider",
        lambda: FakeEmbeddingProvider(),
    )


@pytest.mark.asyncio
async def test_rag_ingest_search_filters_and_delete(db_session, fake_embeddings):
    service = rag_module.RAGService(db_session)
    empty_fingerprint = await service.knowledge_fingerprint()

    document = await service.ingest_text(
        content="Carrier 38AKS codigo E7: falla del sensor del evaporador.",
        title="Manual Carrier 38AKS",
        source="manual-carrier.pdf",
        doc_type="manual",
        manufacturer="Carrier",
        equipment_model="38AKS",
        category="hvac",
    )
    await db_session.commit()
    ingested_fingerprint = await service.knowledge_fingerprint()
    assert ingested_fingerprint != empty_fingerprint

    results = await service.search(
        "Que significa E7 en Carrier 38AKS?",
        manufacturer="Carrier",
        equipment_model="38AKS",
        category="hvac",
    )
    assert len(results) == 1
    assert results[0]["document_title"] == "Manual Carrier 38AKS"
    assert results[0]["manufacturer"] == "Carrier"
    assert results[0]["equipment_model"] == "38AKS"
    assert results[0]["similarity"] > 0.99

    no_results = await service.search(
        "Que significa E7 en Carrier 38AKS?",
        manufacturer="Daikin",
    )
    assert no_results == []

    deleted = await service.delete_document(document.id)
    await db_session.commit()
    assert deleted is True
    deleted_fingerprint = await service.knowledge_fingerprint()
    assert deleted_fingerprint != ingested_fingerprint

    chunk_count = await db_session.scalar(select(func.count()).select_from(KnowledgeChunk))
    assert chunk_count == 0


@pytest.mark.asyncio
async def test_rag_search_boosts_exact_technical_terms(db_session, fake_embeddings):
    document = KnowledgeDocument(
        id=uuid.uuid4(),
        title="Guia Tecnica de Instalacion de Evaporadores RGC",
        source="rgc.pdf",
        doc_type="manual",
        manufacturer="RGC",
        equipment_model="",
        category="refrigeration",
        metadata_={"characters": 1200},
        chunk_count=2,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(document)
    db_session.add_all([
        KnowledgeChunk(
            id=uuid.uuid4(),
            document_id=document.id,
            content=(
                "Guia Tecnica de Instalacion de Evaporadores RGC. "
                "Recomendaciones generales para montaje de evaporadores."
            ),
            chunk_index=0,
            manufacturer="RGC",
            equipment_model="",
            category="refrigeration",
            embedding=[1.0] + [0.0] * 383,
            created_at=datetime.now(timezone.utc),
        ),
        KnowledgeChunk(
            id=uuid.uuid4(),
            document_id=document.id,
            content=(
                "Ubicacion del bulbo de la valvula de expansion: fijar el "
                "bulbo en la linea de succion. Nunca dejarlo colgando en el "
                "aire. Montarlo antes del tubo ecualizador."
            ),
            chunk_index=1,
            manufacturer="RGC",
            equipment_model="",
            category="refrigeration",
            embedding=[0.55, 0.835] + [0.0] * 382,
            created_at=datetime.now(timezone.utc),
        ),
    ])
    await db_session.commit()

    service = rag_module.RAGService(db_session)
    results = await service.search(
        "Estoy instalando un evaporador RGC pero no se la ubicacion del bulbo "
        "de la valvula de expansion",
        limit=1,
    )

    assert len(results) == 1
    assert "bulbo en la linea de succion" in results[0]["content"]


@pytest.mark.asyncio
async def test_glossary_endpoint_lists_metadata_without_chunk_content(
    db_session,
    fake_embeddings,
):
    service = rag_module.RAGService(db_session)
    await service.ingest_text(
        content="Carrier 38AKS codigo E7: falla del sensor del evaporador.",
        title="Manual Carrier 38AKS",
        source="manual-carrier.pdf",
        doc_type="manual",
        manufacturer="Carrier",
        equipment_model="38AKS",
        category="hvac",
    )
    await db_session.commit()

    app = FastAPI()
    app.include_router(knowledge_router, prefix="/knowledge")

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/knowledge/glossary",
            params={"manufacturer": "Carrier", "search": "38AKS"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    document = body["documents"][0]
    assert document["title"] == "Manual Carrier 38AKS"
    assert document["source"] == "manual-carrier.pdf"
    assert document["chunk_count"] == 1
    assert document["metadata"]["characters"] > 0
    assert "content" not in document
    assert "Carrier 38AKS codigo E7" not in response.text
