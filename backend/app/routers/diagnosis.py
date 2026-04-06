"""
Endpoints de Diagnóstico — Análisis de imágenes de equipos.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.diagnosis import DiagnosisResponse
from app.services.vision_service import VisionService

router = APIRouter()


@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_image(
    image: UploadFile = File(..., description="Imagen del equipo a diagnosticar"),
    context: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Analizar una imagen de un equipo HVAC/R.
    Retorna diagnóstico, posibles problemas y recomendaciones.
    """
    service = VisionService(db)
    result = await service.analyze(image, context)
    return result
