"""
Proveedor AI: Claude API directa (desarrollo y producción).
Usa httpx para comunicación async con la API de Anthropic.
Optimizado para ahorro de costos en desarrollo.
"""

import base64
import json
from typing import AsyncIterator

import httpx

from app.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    ChatStreamEvent,
    EmbeddingResponse,
)
from app.config import get_settings


class ClaudeProvider(AIProvider):
    """
    Proveedor usando la API directa de Anthropic.
    Modelo: Claude Haiku (el más económico) para desarrollo.

    Costos aproximados (Haiku):
    - Input:  $0.25 / 1M tokens
    - Output: $1.25 / 1M tokens
    - Una conversación típica (~500 tokens) cuesta ~$0.001
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.anthropic_api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.chat_model = settings.claude_chat_model
        self.vision_model = settings.claude_vision_model
        self.api_version = "2023-06-01"

        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json",
        }

    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ChatResponse:
        """Chat usando Claude API."""
        system_prompt = None
        claude_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        body = {
            "model": self.chat_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": claude_messages,
        }

        if system_prompt:
            body["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=body,
            )
            response.raise_for_status()
            result = response.json()

        return ChatResponse(
            content=result["content"][0]["text"],
            model=result["model"],
            tokens_input=result["usage"]["input_tokens"],
            tokens_output=result["usage"]["output_tokens"],
            finish_reason=result.get("stop_reason"),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[ChatStreamEvent]:
        """Chat con streaming usando Claude API."""
        system_prompt = None
        claude_messages = []
        model = self.chat_model
        tokens_input = 0
        tokens_output = 0
        finish_reason = None

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        body = {
            "model": self.chat_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": claude_messages,
            "stream": True,
        }

        if system_prompt:
            body["system"] = system_prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                self.api_url,
                headers=self.headers,
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data["type"] == "message_start":
                            message = data.get("message", {})
                            usage = message.get("usage", {})
                            model = message.get("model", model)
                            tokens_input = usage.get("input_tokens", 0)
                        elif data["type"] == "content_block_delta":
                            text = data["delta"].get("text", "")
                            if text:
                                yield ChatStreamEvent(type="delta", content=text)
                        elif data["type"] == "message_delta":
                            delta = data.get("delta", {})
                            usage = data.get("usage", {})
                            finish_reason = delta.get("stop_reason")
                            tokens_output = usage.get(
                                "output_tokens",
                                tokens_output,
                            )
                        elif data["type"] == "message_stop":
                            yield ChatStreamEvent(
                                type="done",
                                model=model,
                                tokens_input=tokens_input,
                                tokens_output=tokens_output,
                                finish_reason=finish_reason,
                            )

    async def vision(
        self,
        image_data: bytes,
        prompt: str,
        temperature: float = 0.3,
    ) -> ChatResponse:
        """Análisis de imagen usando Claude Vision."""
        image_b64 = base64.b64encode(image_data).decode("utf-8")

        body = {
            "model": self.vision_model,
            "max_tokens": 1024,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=body,
            )
            response.raise_for_status()
            result = response.json()

        return ChatResponse(
            content=result["content"][0]["text"],
            model=result["model"],
            tokens_input=result["usage"]["input_tokens"],
            tokens_output=result["usage"]["output_tokens"],
            finish_reason=result.get("stop_reason"),
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        """
        Generar embedding usando Voyage AI (partner de Anthropic).
        Anthropic no tiene API de embeddings propia, usamos pgvector
        con un modelo local ligero o Voyage AI en producción.

        Por ahora retornamos un placeholder — los embeddings se
        implementarán cuando configuremos el pipeline RAG completo.
        """
        raise NotImplementedError(
            "Embeddings no disponibles vía Claude API directa. "
            "Se implementará con Voyage AI o modelo local para RAG."
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Batch embeddings — pendiente de implementar."""
        raise NotImplementedError(
            "Embeddings batch no disponible. Pendiente de configurar Voyage AI."
        )

    async def health_check(self) -> bool:
        """Verificar que la API de Claude está accesible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Enviar un mensaje mínimo para verificar la API key
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": self.chat_model,
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "hi"}],
                    },
                )
                return response.status_code == 200
        except Exception:
            return False
