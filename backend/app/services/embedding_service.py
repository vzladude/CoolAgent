"""
Servicio de Embeddings — Generación y búsqueda semántica para RAG.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider
from app.ai.providers.base import EmbeddingResponse


class EmbeddingService:
    """Servicio para generar embeddings y realizar búsqueda semántica con pgvector."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_ai_provider()

    async def generate_embedding(self, content: str) -> list[float]:
        """Generar embedding para un texto."""
        response = await self.provider.embed(content)
        return response.embedding

    async def generate_embeddings_batch(
        self, texts: list[str]
    ) -> list[list[float]]:
        """Generar embeddings para múltiples textos."""
        responses = await self.provider.embed_batch(texts)
        return [r.embedding for r in responses]

    async def search_similar(
        self,
        query: str,
        table: str = "knowledge_chunks",
        limit: int = 5,
        similarity_threshold: float = 0.7,
    ) -> list[dict]:
        """
        Búsqueda semántica usando pgvector.
        Retorna los chunks más similares a la query.
        """
        # Generar embedding de la query
        query_embedding = await self.generate_embedding(query)

        # Búsqueda por similitud coseno en pgvector
        result = await self.db.execute(
            text(f"""
                SELECT
                    id,
                    content,
                    chunk_metadata,
                    1 - (embedding <=> :embedding::vector) as similarity
                FROM {table}
                WHERE 1 - (embedding <=> :embedding::vector) > :threshold
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """),
            {
                "embedding": str(query_embedding),
                "threshold": similarity_threshold,
                "limit": limit,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "content": row.content,
                "metadata": row.chunk_metadata,
                "similarity": float(row.similarity),
            }
            for row in rows
        ]
