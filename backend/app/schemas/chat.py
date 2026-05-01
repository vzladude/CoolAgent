"""
Chat and technical case schemas.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


TechnicalCaseStatus = Literal["open", "closed"]


class TechnicalCaseCreate(BaseModel):
    title: str | None = Field(None, max_length=200)
    manufacturer: str | None = Field(None, max_length=200)
    equipment_model: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=100)
    status: TechnicalCaseStatus = "open"


class TechnicalCaseUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    manufacturer: str | None = Field(None, max_length=200)
    equipment_model: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=100)
    status: TechnicalCaseStatus | None = None


class TechnicalCaseResponse(BaseModel):
    id: UUID
    title: str | None
    manufacturer: str | None = None
    equipment_model: str | None = None
    category: str | None = None
    status: str = "open"
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ChatMessageResponse(BaseModel):
    id: UUID
    technical_case_id: UUID
    conversation_id: UUID | None = None
    role: str
    content: str
    tokens_used: int | None = None
    model_used: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def fill_legacy_conversation_id(self):
        if self.conversation_id is None:
            self.conversation_id = self.technical_case_id
        return self

    model_config = {"from_attributes": True}


class ChatMessageListResponse(BaseModel):
    messages: list[ChatMessageResponse]
    count: int
    limit: int
    offset: int


# Legacy names kept for temporary /conversations wrappers.
ConversationCreate = TechnicalCaseCreate
ConversationResponse = TechnicalCaseResponse
