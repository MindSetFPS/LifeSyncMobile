"""Snapshot inmutable del historial clínico de emergencia.

El contenido se genera en el servidor (patrón Strategy) y nunca se registra en
logs. Solo se persiste el hash del token de descarga, jamás el token en claro.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutils import utcnow
from app.models.base import Base
from app.models.enums import ExportFormat, ExportSection, ExportStatus


def _uuid() -> str:
    return str(uuid.uuid4())


class EmergencyExport(Base):
    __tablename__ = "emergency_exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    format: Mapped[ExportFormat] = mapped_column(
        Enum(
            ExportFormat,
            native_enum=False,
            create_constraint=True,
            name="export_format",
        ),
        nullable=False,
    )
    status: Mapped[ExportStatus] = mapped_column(
        Enum(
            ExportStatus,
            native_enum=False,
            create_constraint=True,
            name="export_status",
        ),
        default=ExportStatus.PENDING,
        nullable=False,
    )
    sections: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    strategy: Mapped[str] = mapped_column(String(40), nullable=False)
    strategy_version: Mapped[str] = mapped_column(String(10), nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    record_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    download_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(40), nullable=True)

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            ExportStatus.FAILED,
            ExportStatus.EXPIRED,
            ExportStatus.REVOKED,
        }

    @property
    def selected_sections(self) -> list[ExportSection]:
        return [ExportSection(value) for value in self.sections]

    def __repr__(self) -> str:
        return f"<EmergencyExport id={self.id!r} format={self.format} status={self.status}>"
