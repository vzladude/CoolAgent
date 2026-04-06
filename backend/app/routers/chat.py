"""
Endpoints de Chat — Conversaciones con el asistente AI.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear una nueva conversación."""
    service = ChatService(db)
    conversation = await service.create_conversation(data)
    return conversation


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
)
async def send_message(
    conversation_id: UUID,
    data: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Enviar un mensaje y obtener respuesta del AI."""
    service = ChatService(db)
    response = await service.send_message(conversation_id, data)
    return response
