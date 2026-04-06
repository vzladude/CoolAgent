"""
Factory para crear el proveedor AI correcto según configuración.
"""

from functools import lru_cache

from app.ai.providers.base import AIProvider
from app.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    """
    Retorna el proveedor AI adecuado según configuración.
    - claude   → ClaudeProvider (API directa, recomendado para desarrollo)
    - ollama   → OllamaProvider (local, requiere GPU)
    - bedrock  → BedrockProvider (AWS, producción)
    """
    settings = get_settings()
    provider_name = settings.ai_provider

    if provider_name == "claude":
        from app.ai.providers.claude_provider import ClaudeProvider
        return ClaudeProvider()

    elif provider_name == "ollama":
        from app.ai.providers.ollama_provider import OllamaProvider
        return OllamaProvider()

    elif provider_name == "bedrock":
        from app.ai.providers.bedrock_provider import BedrockProvider
        return BedrockProvider()

    else:
        raise ValueError(f"Proveedor AI desconocido: {provider_name}")
