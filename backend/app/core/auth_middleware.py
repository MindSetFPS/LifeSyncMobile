"""Middleware global de autenticación Bearer.

Toda ruta bajo `/api/v1` exige un access token JWT válido, salvo las rutas
públicas de autenticación, OAuth y discovery. El middleware valida la firma y
el `type=access`; la carga del usuario y la propiedad del recurso siguen
resolviéndose en la capa de dependencias/repositorios.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core import security
from app.core.config import settings

PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/health",
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        f"{settings.API_V1_PREFIX}/auth/register",
        f"{settings.API_V1_PREFIX}/auth/token",
        f"{settings.API_V1_PREFIX}/auth/refresh",
        f"{settings.API_V1_PREFIX}/auth/revoke",
        f"{settings.API_V1_PREFIX}/auth/introspect",
        f"{settings.API_V1_PREFIX}/oauth/authorize",
    }
)

PUBLIC_PREFIXES: tuple[str, ...] = ("/.well-known",)


def is_public_path(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    return any(path == prefix or path.startswith(f"{prefix}/")
               for prefix in PUBLIC_PREFIXES)


def _unauthorized() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "No se pudieron validar las credenciales"},
        headers={"WWW-Authenticate": "Bearer"},
    )


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        if not path.startswith(settings.API_V1_PREFIX) or is_public_path(path):
            return await call_next(request)

        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return _unauthorized()

        try:
            request.state.token_payload = security.decode_token(
                token.strip(), expected_type="access"
            )
        except security.TokenError:
            return _unauthorized()

        return await call_next(request)


__all__ = ["BearerAuthMiddleware", "is_public_path"]
