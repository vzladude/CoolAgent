"""
Proveedor AI: Ollama (desarrollo local).
Usa la librería oficial de Ollama con httpx para comunicación async.
"""

import base64
from typing import AsyncIterator

import httpx
from ollama import AsyncClient

from app.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
)
from app.config import get_settings


class OllamaProvider(AIProvider):
    """
    Proveedor local usando Ollama.
    Modelos: Qwen 3.5 (chat), Qwen2.5-VL (visión), qwen3-embedding (embeddings).
    """

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.chat_model = settings.ollama_chat_model
        self.vision_model = settings.ollama_vision_model
        self.embedding_model = settings.ollama_embedding_model
        self.client = AsyncClient(host=self.base_url)

    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ChatResponse:
        """Chat usando Ollama."""
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat(
            model=self.chat_model,
            messages=ollama_messages,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )

        return ChatResponse(
            content=response["message"]["content"],
            model=self.chat_model,
            tokens_input=response.get("prompt_eval_count", 0),
            tokens_output=response.get("eval_count", 0),
            finish_reason=response.get("done_reason"),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Chat con streaming usando Ollama."""
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self.client.chat(
            model=self.chat_model,
            messages=ollama_messages,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        )

        async for chunk in stream:
            if chunk["message"]["content"]:
                yield chunk["message"]["content"]

    async def vision(
        self,
        image_data: bytes,
        prompt: str,
        temperature: float = 0.3,
    ) -> ChatResponse:
        """Análisis de imagen usando Qwen2.5-VL."""
        image_b64 = base64.b64encode(image_data).decode("utf-8")

        response = await self.client.chat(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
            options={
                "temperature": temperature,
            },
        )

        return ChatResponse(
            content=response["message"]["content"],
            model=self.vision_model,
            tokens_input=response.get("prompt_eval_count", 0),
            tokens_output=response.get("eval_count", 0),
            finish_reason=response.get("done_reason"),
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generar embedding con qwen3-embedding."""
        response = await self.client.embed(
            model=self.embedding_model,
            input=text,
        )

        embedding = response["embeddings"][0]
        return EmbeddingResponse(
            embedding=embedding,
            model=self.embedding_model,
            dimensions=len(embedding),
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Generar embeddings en batch."""
        response = await self.client.embed(
            model=self.embedding_model,
            input=texts,
        )

        return [
            EmbeddingResponse(
                embedding=emb,
                model=self.embedding_model,
                dimensions=len(emb),
            )
            for emb in response["embeddings"]
        ]

    async def health_check(self) -> bool:
        """Verificar que Ollama está disponible."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception:
            return False
