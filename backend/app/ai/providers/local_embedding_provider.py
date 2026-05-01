"""
Proveedor de Embeddings local usando sentence-transformers.
Corre en CPU dentro de la API — no requiere GPU ni servicio externo.

Modelo: all-MiniLM-L6-v2
- Dimensiones: 384
- RAM: ~80MB
- Velocidad: ~5ms por texto en CPU
- Calidad: Excelente para búsqueda semántica en español e inglés
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.ai.providers.base import EmbeddingResponse


class LocalEmbeddingProvider:
    """
    Proveedor de embeddings local usando sentence-transformers.
    Se usa para el pipeline RAG independientemente del proveedor de chat.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimensions = self.model.get_sentence_embedding_dimension()

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generar embedding para un texto."""
        embedding = self.model.encode(text, normalize_embeddings=True).tolist()
        return EmbeddingResponse(
            embedding=embedding,
            model=self.model_name,
            dimensions=self.dimensions,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Generar embeddings para múltiples textos (muy eficiente en batch)."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        ).tolist()

        return [
            EmbeddingResponse(
                embedding=emb,
                model=self.model_name,
                dimensions=self.dimensions,
            )
            for emb in embeddings
        ]


@lru_cache
def get_embedding_provider() -> LocalEmbeddingProvider:
    """Singleton del proveedor de embeddings."""
    return LocalEmbeddingProvider()
