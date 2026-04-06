"""
Servicio de Visión — Diagnóstico de equipos por imagen.
"""

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers import get_ai_provider
from app.ai.prompts import SYSTEM_PROMPT_VISION
from app.schemas.diagnosis import DiagnosisResponse


class VisionService:
    """Servicio para análisis de imágenes de equipos HVAC/R."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_ai_provider()

    async def analyze(
        self,
        image: UploadFile,
        context: str | None = None,
    ) -> DiagnosisResponse:
        """
        Analizar imagen de un equipo y retornar diagnóstico.
        """
        # Leer datos de la imagen
        image_data = await image.read()

        # Construir prompt con contexto opcional
        prompt = SYSTEM_PROMPT_VISION
        if context:
            prompt += f"\n\nContexto adicional del técnico: {context}"

        prompt += """

Responde EXCLUSIVAMENTE en formato JSON con esta estructura:
{
    "equipment_type": "tipo de equipo detectado",
    "diagnosis": "diagnóstico principal",
    "possible_issues": ["problema 1", "problema 2"],
    "recommendations": ["recomendación 1", "recomendación 2"],
    "confidence": 0.85
}"""

        # Enviar al modelo de visión
        response = await self.provider.vision(
            image_data=image_data,
            prompt=prompt,
            temperature=0.3,
        )

        # Parsear respuesta JSON del modelo
        try:
            # Intentar extraer JSON de la respuesta
            content = response.content
            # Buscar el JSON en la respuesta (puede venir envuelto en markdown)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            parsed = json.loads(content.strip())
        except (json.JSONDecodeError, IndexError):
            # Fallback si el modelo no retorna JSON válido
            parsed = {
                "equipment_type": None,
                "diagnosis": response.content,
                "possible_issues": [],
                "recommendations": [],
                "confidence": 0.5,
            }

        return DiagnosisResponse(
            id=uuid4(),
            equipment_type=parsed.get("equipment_type"),
            diagnosis=parsed["diagnosis"],
            possible_issues=parsed.get("possible_issues", []),
            recommendations=parsed.get("recommendations", []),
            confidence=parsed.get("confidence", 0.5),
            model_used=response.model,
            created_at=datetime.now(timezone.utc),
        )
