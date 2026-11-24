"""Campos comunes a los registros clínicos sincronizables.

El `id` puede generarse en el dispositivo para permitir creación offline; el
servidor lo valida pero nunca lo usa para autorizar. El dueño (`user_id`) se
deriva siempre del JWT, nunca del cuerpo de la petición.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutils import utcnow


def _uuid() -> str:
    return str(uuid.uuid4())


class HealthRecordMixin:
    """Identidad, propiedad, auditoría y control de concurrencia."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
