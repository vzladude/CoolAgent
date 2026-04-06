"""
Interfaz abstracta para proveedores de AI.
Strategy Pattern: permite intercambiar Ollama ↔ Bedrock sin cambiar lógica de negocio.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class ChatMessage:
    """Mensaje en una conversación."""
    role: str       # "system" | "user" | "assistant"
    content: str
    images: list[bytes] | None = None  # Para mensajes con imágenes (vision)


@dataclass
class ChatResponse:
    """Respuesta del modelo AI."""
    content: str
    model: str
    tokens_input: int
    tokens_output: int
    finish_reason: str | None = None


@dataclass
class EmbeddingResponse:
    """Respuesta de embeddings."""
    embedding: list[float]
    model: str
    dimensions: int


class AIProvider(ABC):
    """
    Interfaz base para todos los proveedores de AI.
    Implementaciones: OllamaProvider, BedrockProvider.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ChatResponse:
        """Generar respuesta de chat (sin streaming)."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Generar respuesta de chat con streaming."""
        ...

    @abstractmethod
    async def vision(
        self,
        image_data: bytes,
        prompt: str,
        temperature: float = 0.3,
    ) -> ChatResponse:
        """Analizar una imagen con el modelo de visión."""
        ...

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> EmbeddingResponse:
        """Generar embedding para un texto."""
        ...

    @abstractmethod
    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResponse]:
        """Generar embeddings para múltiples textos."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verificar que el proveedor está disponible."""
        ...
