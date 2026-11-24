"""Cliente OAuth registrado.

`client_secret` se persiste solo como hash bcrypt (nunca en claro). Los
clientes públicos (app móvil) no tienen secreto y se autentican únicamente
con PKCE, como exige RFC 8252 para aplicaciones nativas.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutils import utcnow
from app.models.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_id: Mapped[str] = mapped_column(
        String(80), unique=True, index=True, nullable=False
    )
    client_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_secret: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    redirect_uris: Mapped[str] = mapped_column(Text, default="", nullable=False)
    allowed_scopes: Mapped[str] = mapped_column(
        String(255), default="read write", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    @property
    def redirect_uri_list(self) -> list[str]:
        return [uri.strip() for uri in self.redirect_uris.splitlines() if uri.strip()]

    @property
    def scope_list(self) -> list[str]:
        return [scope for scope in self.allowed_scopes.split() if scope]

    def __repr__(self) -> str:
        return f"<OAuthClient client_id={self.client_id!r} public={self.is_public}>"
