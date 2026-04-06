"""
Endpoints de Códigos de Error — Base de datos de errores por fabricante/modelo.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.error_codes import ErrorCodeResponse, ManufacturerResponse

router = APIRouter()


@router.get("/", response_model=list[ErrorCodeResponse])
async def search_error_codes(
    code: str | None = Query(None, description="Código de error a buscar"),
    manufacturer: str | None = Query(None, description="Filtrar por fabricante"),
    model: str | None = Query(None, description="Filtrar por modelo"),
    db: AsyncSession = Depends(get_db),
):
    """Buscar códigos de error con filtros opcionales."""
    # TODO: Implementar lógica de búsqueda
    return []


@router.get("/manufacturers", response_model=list[ManufacturerResponse])
async def list_manufacturers(
    db: AsyncSession = Depends(get_db),
):
    """Listar todos los fabricantes disponibles."""
    # TODO: Implementar
    return []
