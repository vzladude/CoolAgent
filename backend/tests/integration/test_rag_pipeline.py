from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.ai.providers.base import EmbeddingResponse
from app.database import get_db
from app.models.knowledge import KnowledgeChunk
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

    chunk_count = await db_session.scalar(select(func.count()).select_from(KnowledgeChunk))
    assert chunk_count == 0


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
