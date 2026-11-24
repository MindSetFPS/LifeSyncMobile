"""Utilidades del protocolo OAuth 2.0.

Centraliza los errores normalizados de RFC 6749 §5.2, la autenticación de
clientes por HTTP Basic (RFC 7617) y la validación de scopes.
"""

from __future__ import annotations

import base64
import binascii

from fastapi import Request
from fastapi.responses import JSONResponse

OAUTH_NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


class OAuthError(Exception):
    """Error del protocolo OAuth 2.0 con código y descripción legibles."""

    def __init__(
        self,
        error: str,
        description: str | None = None,
        *,
        status_code: int = 400,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(description or error)
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers or {}


async def oauth_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Traduce un `OAuthError` al cuerpo JSON que exige RFC 6749."""
    assert isinstance(exc, OAuthError)
    body: dict[str, str] = {"error": exc.error}
    if exc.description:
        body["error_description"] = exc.description
    if exc.error == "invalid_client":
        body["error_description"] = body.get("error_description", "Cliente no autenticado")
    headers = {**OAUTH_NO_STORE, **exc.headers}
    return JSONResponse(body, status_code=exc.status_code, headers=headers)


def parse_basic_authorization(header: str | None) -> tuple[str, str] | None:
    """Extrae `client_id`/`client_secret` de `Authorization: Basic ...`."""
    if not header:
        return None
    scheme, _, encoded = header.partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return None
    try:
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        raise OAuthError("invalid_client", "Cabecera Basic mal formada", status_code=401) from None
    client_id, sep, client_secret = decoded.partition(":")
    if not sep or not client_id:
        raise OAuthError("invalid_client", "Cabecera Basic mal formada", status_code=401)
    return client_id, client_secret


def parse_scope(raw: str | None) -> list[str]:
    """Divide una cadena de scopes separada por espacios, sin duplicados."""
    if not raw:
        return []
    return list(dict.fromkeys(part for part in raw.split() if part))


__all__ = [
    "OAUTH_NO_STORE",
    "OAuthError",
    "oauth_error_handler",
    "parse_basic_authorization",
    "parse_scope",
]
