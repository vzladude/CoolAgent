"""
Modelos de Códigos de Error — Base de datos de errores HVAC/R.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Manufacturer(Base):
    """Fabricante de equipos HVAC/R."""
    __tablename__ = "manufacturers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación
    error_codes: Mapped[list["ErrorCode"]] = relationship(
        back_populates="manufacturer_rel", cascade="all, delete-orphan"
    )


class ErrorCode(Base):
    """Código de error de un equipo HVAC/R."""
    __tablename__ = "error_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(Text)
    manufacturer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("manufacturers.id", ondelete="CASCADE"),
    )
    manufacturer: Mapped[str] = mapped_column(String(200))
    model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # low | medium | high | critical
    possible_causes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación
    manufacturer_rel: Mapped["Manufacturer"] = relationship(
        back_populates="error_codes"
    )
