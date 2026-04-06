"""
Servicio de Chat — Lógica de negocio para conversaciones con el AI.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.providers import get_ai_provider
from app.ai.providers.base import ChatMessage
from app.ai.prompts import SYSTEM_PROMPT_CHAT
from app.models.conversation import Conversation, Message
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
)


class ChatService:
    """Servicio para gestionar conversaciones con el asistente AI."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_ai_provider()

    async def create_conversation(
        self, data: ConversationCreate
    ) -> ConversationResponse:
        """Crear una nueva conversación."""
        conversation = Conversation(
            id=uuid4(),
            title=data.title or "Nueva conversación",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(conversation)
        await self.db.flush()

        return ConversationResponse.model_validate(conversation)

    async def send_message(
        self,
        conversation_id: UUID,
        data: ChatMessageRequest,
    ) -> ChatMessageResponse:
        """Enviar mensaje del usuario y obtener respuesta del AI."""
        # Verificar que la conversación existe
        conversation = await self.db.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversación {conversation_id} no encontrada")

        # Guardar mensaje del usuario
        user_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="user",
            content=data.content,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(user_message)

        # Obtener historial de la conversación
        history = await self._get_conversation_history(conversation_id)

        # Construir mensajes para el AI
        ai_messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT_CHAT),
            *[
                ChatMessage(role=msg.role, content=msg.content)
                for msg in history
            ],
            ChatMessage(role="user", content=data.content),
        ]

        # Obtener respuesta del AI
        response = await self.provider.chat(ai_messages)

        # Guardar respuesta del asistente
        assistant_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            tokens_used=response.tokens_input + response.tokens_output,
            model_used=response.model,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(assistant_message)
        await self.db.flush()

        return ChatMessageResponse.model_validate(assistant_message)

    async def _get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 20,
    ) -> list[Message]:
        """Obtener los últimos N mensajes de una conversación."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # Orden cronológico
        return messages
