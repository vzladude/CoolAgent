"""
Usage tracking models.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UsageEvent(Base):
    """A single usage event for monitoring tokens, cache and provider calls."""

    __tablename__ = "usage_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), default="chat", index=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(150), nullable=True)
    prompt_policy_version: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    cache_status: Mapped[str] = mapped_column(String(20), default="miss", index=True)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    tokens_total: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 8), nullable=True
    )
    cache_saved_tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    cache_saved_tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    cache_saved_tokens_total: Mapped[int] = mapped_column(Integer, default=0)
    cache_saved_cost_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 8), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
