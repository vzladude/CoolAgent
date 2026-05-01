"""
Endpoints de Knowledge Base — Administración de documentos para RAG.
Todos los filtros (manufacturer, equipment_model, category) son opcionales.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.knowledge import KnowledgeGlossaryResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(..., description="Archivo PDF a ingestar"),
    title: str = Form(..., description="Título del documento"),
    source: str = Form(None, description="Fuente u origen del documento"),
    doc_type: str = Form("general", description="Tipo: general, manual, datasheet, guide, faq, book"),
    manufacturer: str = Form(None, description="Fabricante (ej: Carrier, Daikin). Opcional"),
    equipment_model: str = Form(None, description="Modelo de equipo (ej: 38AKS). Opcional"),
    category: str = Form(None, description="Categoría (ej: refrigeration, hvac, electrical). Opcional"),
    db: AsyncSession = Depends(get_db),
):
    """
    Subir un PDF para ingestarlo en la knowledge base.
    Filtros opcionales: si es un manual de un equipo específico, indicar fabricante y modelo.
    Si es un libro general de refrigeración, dejar esos campos vacíos.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    service = RAGService(db)

    try:
        document = await service.ingest_pdf(
            file=file.file,
            title=title,
            source=source,
            doc_type=doc_type,
            manufacturer=manufacturer,
            equipment_model=equipment_model,
            category=category,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "status": "success",
        "document_id": str(document.id),
        "title": document.title,
        "manufacturer": document.manufacturer,
        "equipment_model": document.equipment_model,
        "category": document.category,
        "chunks_created": document.chunk_count,
        "message": f"Documento '{title}' procesado con {document.chunk_count} chunks.",
    }


@router.post("/upload/text")
async def upload_text(
    title: str = Form(..., description="Título del documento"),
    content: str = Form(..., description="Contenido de texto a ingestar"),
    source: str = Form(None, description="Fuente u origen"),
    doc_type: str = Form("guide", description="Tipo: general, manual, datasheet, guide, faq, book"),
    manufacturer: str = Form(None, description="Fabricante. Opcional"),
    equipment_model: str = Form(None, description="Modelo de equipo. Opcional"),
    category: str = Form(None, description="Categoría. Opcional"),
    db: AsyncSession = Depends(get_db),
):
    """Ingestar texto plano directamente en la knowledge base."""
    service = RAGService(db)
    document = await service.ingest_text(
        content=content,
        title=title,
        source=source,
        doc_type=doc_type,
        manufacturer=manufacturer,
        equipment_model=equipment_model,
        category=category,
    )

    return {
        "status": "success",
        "document_id": str(document.id),
        "title": document.title,
        "chunks_created": document.chunk_count,
    }


@router.get("/documents")
async def list_documents(
    manufacturer: str | None = Query(None, description="Filtrar por fabricante"),
    category: str | None = Query(None, description="Filtrar por categoría"),
    db: AsyncSession = Depends(get_db),
):
    """Listar documentos, opcionalmente filtrados por fabricante o categoría."""
    service = RAGService(db)
    return await service.list_documents(
        manufacturer=manufacturer,
        category=category,
    )


@router.get("/glossary", response_model=KnowledgeGlossaryResponse)
async def glossary(
    manufacturer: str | None = Query(None, description="Filtrar por fabricante"),
    category: str | None = Query(None, description="Filtrar por categorÃ­a"),
    doc_type: str | None = Query(None, description="Filtrar por tipo de documento"),
    search: str | None = Query(None, description="Buscar en tÃ­tulo o fuente"),
    db: AsyncSession = Depends(get_db),
):
    """
    Glosario vivo de documentos que alimentan el RAG.

    Expone metadata/procedencia de documentos, sin devolver contenido completo
    de chunks.
    """
    service = RAGService(db)
    documents = await service.glossary(
        manufacturer=manufacturer,
        category=category,
        doc_type=doc_type,
        search=search,
    )
    return {"documents": documents, "count": len(documents)}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Eliminar un documento y todos sus chunks."""
    service = RAGService(db)
    deleted = await service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return {"status": "deleted", "document_id": str(document_id)}


@router.post("/search")
async def search_knowledge(
    query: str = Form(..., description="Texto a buscar"),
    limit: int = Form(5, description="Número máximo de resultados"),
    manufacturer: str = Form(None, description="Filtrar por fabricante. Opcional"),
    equipment_model: str = Form(None, description="Filtrar por modelo. Opcional"),
    category: str = Form(None, description="Filtrar por categoría. Opcional"),
    db: AsyncSession = Depends(get_db),
):
    """
    Buscar en la knowledge base por similitud semántica.
    Filtros opcionales acotan la búsqueda (ej: solo manuales Carrier).
    """
    service = RAGService(db)
    results = await service.search(
        query,
        limit=limit,
        manufacturer=manufacturer,
        equipment_model=equipment_model,
        category=category,
    )
    return {"query": query, "results": results, "count": len(results)}
