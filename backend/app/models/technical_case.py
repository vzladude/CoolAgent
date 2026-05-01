"""
Technical case models for chat workflows.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TechnicalCase(Base):
    """A field-service technical case that owns a chat history."""

    __tablename__ = "technical_cases"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'closed')",
            name="ck_technical_cases_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    equipment_model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="open",
        server_default="open",
        index=True,
    )
    context_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_until_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    summary_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    summary_model: Mapped[str | None] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="technical_case", cascade="all, delete-orphan"
    )


class Message(Base):
    """A chat message that belongs to a technical case."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    technical_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("technical_cases.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    technical_case: Mapped["TechnicalCase"] = relationship(back_populates="messages")

    @property
    def conversation_id(self) -> uuid.UUID:
        """Legacy alias for pre-TechnicalCase code paths."""
        return self.technical_case_id

    @conversation_id.setter
    def conversation_id(self, value: uuid.UUID) -> None:
        self.technical_case_id = value
