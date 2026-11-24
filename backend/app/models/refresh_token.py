"""Sesión de refresh token con rotación y detección de reutilización.

RFC 6749 §10.4 y RFC 6819 §5.2.2.3: cada refresh token se usa una sola vez.
Toda la cadena de rotación comparte una `token_family`; si un token ya
rotado se vuelve a presentar, se revoca la familia completa (posible robo).
Solo se almacena el hash SHA-256 del token.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutils import utcnow
from app.models.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class RefreshTokenSession(Base):
    __tablename__ = "refresh_token_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    family_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(80), nullable=False)
    scope: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_usable(self) -> bool:
        return self.revoked_at is None and self.rotated_at is None

    def __repr__(self) -> str:
        return f"<RefreshTokenSession family={self.family_id!r} revoked={self.revoked_at}>"
