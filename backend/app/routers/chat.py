"""
Chat endpoints for technical cases.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageListResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
    TechnicalCaseCreate,
    TechnicalCaseResponse,
    TechnicalCaseUpdate,
)
from app.services.chat_service import ChatService
from app.services.auth_service import get_optional_current_user

router = APIRouter()


@router.post("/cases", response_model=TechnicalCaseResponse)
async def create_case(
    data: TechnicalCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Crear un caso tecnico."""
    return await ChatService(db, _user_id(current_user)).create_case(data)


@router.get("/cases", response_model=list[TechnicalCaseResponse])
async def list_cases(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Listar casos tecnicos."""
    return await ChatService(db, _user_id(current_user)).list_cases(
        limit=limit,
        offset=offset,
    )


@router.get("/cases/{case_id}", response_model=TechnicalCaseResponse)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Obtener un caso tecnico."""
    return await _case_or_404(ChatService(db, _user_id(current_user)).get_case(case_id))


@router.patch("/cases/{case_id}", response_model=TechnicalCaseResponse)
async def update_case(
    case_id: UUID,
    data: TechnicalCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Actualizar metadata de un caso tecnico."""
    return await _case_or_404(
        ChatService(db, _user_id(current_user)).update_case(case_id, data)
    )


@router.get(
    "/cases/{case_id}/messages",
    response_model=ChatMessageListResponse,
)
async def list_case_messages(
    case_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Listar mensajes paginados de un caso tecnico."""
    return await _case_or_404(
        ChatService(db, _user_id(current_user)).list_messages(
            case_id,
            limit=limit,
            offset=offset,
        )
    )


@router.post(
    "/cases/{case_id}/messages",
    response_model=ChatMessageResponse,
)
async def send_case_message(
    case_id: UUID,
    data: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Enviar un mensaje dentro de un caso tecnico."""
    return await _case_or_404(
        ChatService(db, _user_id(current_user)).send_case_message(case_id, data)
    )


@router.websocket("/cases/{case_id}/messages/stream")
async def stream_case_message(
    websocket: WebSocket,
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Enviar un mensaje y recibir respuesta por streaming WebSocket."""
    await _stream_message(websocket, case_id, ChatService(db))


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Legacy alias: usar POST /cases."""
    return await ChatService(db, _user_id(current_user)).create_conversation(data)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
)
async def send_message(
    conversation_id: UUID,
    data: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Legacy alias: usar POST /cases/{case_id}/messages."""
    return await _case_or_404(
        ChatService(db, _user_id(current_user)).send_message(conversation_id, data)
    )


@router.websocket("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    websocket: WebSocket,
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Legacy alias: usar WebSocket /cases/{case_id}/messages/stream."""
    await _stream_message(websocket, conversation_id, ChatService(db))


async def _stream_message(
    websocket: WebSocket,
    case_id: UUID,
    service: ChatService,
) -> None:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        data = ChatMessageRequest.model_validate(payload)

        async for event in service.stream_case_message(case_id, data):
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


def _user_id(current_user: User | None) -> UUID | None:
    return current_user.id if current_user is not None else None


async def _case_or_404(coro):
    try:
        return await coro
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
