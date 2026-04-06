"""
Configuración centralizada de la aplicación.
Usa pydantic-settings para cargar variables de entorno con validación.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ─── General ─────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    app_name: str = "CoolAgent API"
    api_v1_prefix: str = "/api/v1"

    # ─── Auth ────────────────────────────────────────────
    secret_key: str = "cambiar-en-produccion-por-algo-seguro"
    access_token_expire_minutes: int = 30

    # ─── Database ────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://coolagent:coolagent_dev@localhost:5432/coolagent"

    # ─── Redis ───────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ─── MinIO / S3 ─────────────────────────────────────
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "coolagent"
    minio_secure: bool = False

    # ─── Claude API (desarrollo) ────────────────────────
    anthropic_api_key: str = ""
    claude_chat_model: str = "claude-haiku-4-5-20251001"
    claude_vision_model: str = "claude-haiku-4-5-20251001"

    # ─── Ollama (alternativa local) ──────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen3:4b"
    ollama_vision_model: str = "qwen2.5vl:3b"
    ollama_embedding_model: str = "nomic-embed-text"

    # ─── AWS Bedrock (producción) ────────────────────────
    aws_region: str = "us-east-1"
    bedrock_chat_model: str = "anthropic.claude-3-haiku-20240307-v1:0"
    bedrock_embedding_model: str = "amazon.titan-embed-text-v2:0"

    # ─── AI Provider ────────────────────────────────────
    ai_provider_name: str = "claude"  # claude | ollama | bedrock

    # ─── Rate Limiting ───────────────────────────────────
    rate_limit_chat: int = 50       # mensajes por hora
    rate_limit_vision: int = 20     # imágenes por hora

    @property
    def ai_provider(self) -> str:
        """Selecciona proveedor AI según configuración."""
        return self.ai_provider_name


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración cacheado."""
    return Settings()
