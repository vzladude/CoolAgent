"""
Proveedor AI: AWS Bedrock (producción).
Usa boto3 para comunicación con Claude y Titan.
"""

import json
from typing import AsyncIterator

import boto3

from app.ai.providers.base import (
    AIProvider,
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
)
from app.config import get_settings


class BedrockProvider(AIProvider):
    """
    Proveedor de producción usando AWS Bedrock.
    Modelos: Claude Haiku 3 (chat/visión), Titan Embeddings V2 (embeddings).

    NOTA: Esta es la implementación inicial (stub).
    Se completará durante la Fase 4 (migración a AWS).
    """

    def __init__(self):
        settings = get_settings()
        self.region = settings.aws_region
        self.chat_model = settings.bedrock_chat_model
        self.embedding_model = settings.bedrock_embedding_model

        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region,
        )

    async def chat(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ChatResponse:
        """Chat usando Claude en Bedrock."""
        # Formatear mensajes para la API de Claude (Messages API)
        system_prompt = None
        claude_messages = []

        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                claude_messages.append({
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}],
                })

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": claude_messages,
        }

        if system_prompt:
            body["system"] = system_prompt

        response = self.bedrock_runtime.invoke_model(
            modelId=self.chat_model,
            body=json.dumps(body),
        )

        result = json.loads(response["body"].read())

        return ChatResponse(
            content=result["content"][0]["text"],
            model=self.chat_model,
            tokens_input=result["usage"]["input_tokens"],
            tokens_output=result["usage"]["output_tokens"],
            finish_reason=result.get("stop_reason"),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Chat con streaming usando Bedrock."""
        # TODO: Implementar con invoke_model_with_response_stream
        raise NotImplementedError("Bedrock streaming será implementado en Fase 4")

    async def vision(
        self,
        image_data: bytes,
        prompt: str,
        temperature: float = 0.3,
    ) -> ChatResponse:
        """Análisis de imagen usando Claude Vision en Bedrock."""
        import base64

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
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

        response = self.bedrock_runtime.invoke_model(
            modelId=self.chat_model,
            body=json.dumps(body),
        )

        result = json.loads(response["body"].read())

        return ChatResponse(
            content=result["content"][0]["text"],
            model=self.chat_model,
            tokens_input=result["usage"]["input_tokens"],
            tokens_output=result["usage"]["output_tokens"],
            finish_reason=result.get("stop_reason"),
        )

    async def embed(self, text: str) -> EmbeddingResponse:
        """Generar embedding con Titan Embeddings V2."""
        body = {
            "inputText": text,
        }

        response = self.bedrock_runtime.invoke_model(
            modelId=self.embedding_model,
            body=json.dumps(body),
        )

        result = json.loads(response["body"].read())
        embedding = result["embedding"]

        return EmbeddingResponse(
            embedding=embedding,
            model=self.embedding_model,
            dimensions=len(embedding),
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Generar embeddings en batch (secuencial para Titan)."""
        results = []
        for text in texts:
            result = await self.embed(text)
            results.append(result)
        return results

    async def health_check(self) -> bool:
        """Verificar acceso a Bedrock."""
        try:
            self.bedrock_runtime.list_foundation_models(
                byProvider="anthropic",
            )
            return True
        except Exception:
            return False
