"""
Schemas de Chat — Validación de request/response.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str | None = Field(None, max_length=200)


class ConversationResponse(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str  # "user" | "assistant"
    content: str
    tokens_used: int | None = None
    model_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
