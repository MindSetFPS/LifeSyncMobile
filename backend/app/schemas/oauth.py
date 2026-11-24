"""Esquemas de las respuestas OAuth 2.0 (RFC 6749, 7662, 7009)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    """Respuesta del endpoint de token (RFC 6749 §5.1)."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str | None = None
    scope: str = ""


class TokenRevocationResponse(BaseModel):
    """RFC 7009 §2.2: el cuerpo de la respuesta de revocación va vacío."""


class IntrospectionResponse(BaseModel):
    """RFC 7662 §2.2. `active` es el único campo obligatorio."""

    model_config = ConfigDict(populate_by_name=True)

    active: bool
    scope: str | None = None
    client_id: str | None = None
    token_type: str | None = None
    exp: int | None = None
    iat: int | None = None
    sub: str | None = None
    iss: str | None = None
    jti: str | None = None


class AuthorizationCodeIssue(BaseModel):
    """Resultado interno del canje de un código de autorización."""

    code: str
    redirect_uri: str
    state: str | None = None
