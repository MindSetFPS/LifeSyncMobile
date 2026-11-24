"""Metadatos del servidor de autorización y JWKS.

* RFC 8414: `/.well-known/oauth-authorization-server`
* OpenID Connect Discovery 1.0: `/.well-known/openid-configuration`
* RFC 7517: `/.well-known/jwks.json` con la llave pública RS256
"""

from __future__ import annotations

import base64
import math
from typing import Any

from cryptography.hazmat.primitives import serialization
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core import security
from app.core.config import settings

router = APIRouter(tags=["oauth-metadata"])


def _issuer() -> str:
    return settings.OAUTH_ISSUER.rstrip("/")


def _metadata() -> dict[str, Any]:
    issuer = _issuer()
    scopes = settings.OAUTH_SUPPORTED_SCOPES.split()
    return {
        "issuer": issuer,
        "authorization_endpoint": f"{issuer}{settings.OAUTH_AUTHORIZE_URL}",
        "token_endpoint": f"{issuer}{settings.OAUTH_TOKEN_URL}",
        "revocation_endpoint": f"{issuer}{settings.API_V1_PREFIX}/auth/revoke",
        "introspection_endpoint": f"{issuer}{settings.API_V1_PREFIX}/auth/introspect",
        "jwks_uri": f"{issuer}/.well-known/jwks.json",
        "userinfo_endpoint": f"{issuer}{settings.API_V1_PREFIX}/auth/me",
        "scopes_supported": scopes,
        "response_types_supported": ["code"],
        "response_modes_supported": ["query"],
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
            "password",
        ],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": [
            "none",
            "client_secret_basic",
            "client_secret_post",
        ],
        "revocation_endpoint_auth_methods_supported": [
            "none",
            "client_secret_basic",
            "client_secret_post",
        ],
        "introspection_endpoint_auth_methods_supported": [
            "none",
            "client_secret_basic",
            "client_secret_post",
        ],
        "id_token_signing_alg_values_supported": [settings.JWT_ALGORITHM],
        "subject_types_supported": ["public"],
        "service_documentation": f"{issuer}/docs",
    }


@router.get(
    "/.well-known/oauth-authorization-server",
    summary="Metadatos de autorización (RFC 8414)",
)
async def authorization_server_metadata() -> JSONResponse:
    return JSONResponse(_metadata(), headers={"Cache-Control": "public, max-age=300"})


@router.get(
    "/.well-known/openid-configuration",
    summary="Configuración OpenID Connect Discovery",
)
async def openid_configuration() -> JSONResponse:
    return JSONResponse(_metadata(), headers={"Cache-Control": "public, max-age=300"})


@router.get("/.well-known/jwks.json", summary="JWKS con la llave pública RS256")
async def jwks() -> JSONResponse:
    """Expone `n`/`e` de la llave pública; la privada nunca sale del servidor."""
    public_key = serialization.load_pem_public_key(
        security.public_key_pem().encode("utf-8")
    )
    numbers = public_key.public_numbers()
    key_size = numbers.n.bit_length()

    def _b64(value: int, length: int | None = None) -> str:
        raw = value.to_bytes(length or math.ceil(value.bit_length() / 8), "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    key = {
        "kty": "RSA",
        "use": "sig",
        "alg": settings.JWT_ALGORITHM,
        "kid": settings.JWT_KEY_ID,
        "n": _b64(numbers.n, math.ceil(key_size / 8)),
        "e": _b64(numbers.e),
    }
    return JSONResponse(
        {"keys": [key]}, headers={"Cache-Control": "public, max-age=300"}
    )


__all__ = ["router"]
