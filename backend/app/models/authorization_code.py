"""Código de autorización de un solo uso (RFC 6749 §4.1, PKCE RFC 7636).

Se guarda el hash SHA-256 del código. `code_challenge` nunca se almacena en
claro como verifier: su verificación ocurre en el canje.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutils import utcnow
from app.models.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    code_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(80), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    code_challenge: Mapped[str | None] = mapped_column(String(128), nullable=True)
    code_challenge_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    nonce: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<AuthorizationCode client={self.client_id!r} consumed={self.consumed_at}>"
