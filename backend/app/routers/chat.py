"""
Chat endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
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
    """Crear una nueva conversacion."""
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
    """Enviar un mensaje y obtener respuesta completa del AI."""
    service = ChatService(db)
    response = await service.send_message(conversation_id, data)
    return response


@router.websocket("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    websocket: WebSocket,
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Enviar un mensaje y recibir respuesta por streaming WebSocket."""
    await websocket.accept()
    service = ChatService(db)

    try:
        payload = await websocket.receive_json()
        data = ChatMessageRequest.model_validate(payload)

        async for event in service.stream_message(conversation_id, data):
            await websocket.send_json(event)

        await websocket.close()
    except WebSocketDisconnect:
        raise
    except ValidationError as exc:
        await websocket.send_json({
            "type": "error",
            "message": "Payload invalido",
            "details": exc.errors(),
        })
        await websocket.close(code=1003)
    except ValueError as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close(code=1008)
