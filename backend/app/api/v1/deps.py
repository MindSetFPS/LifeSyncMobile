"""Dependencias de FastAPI para autenticación OAuth 2.0 (Bearer)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.core.oauth import parse_basic_authorization
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.OAUTH_TOKEN_URL)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Devuelve el usuario autenticado.

    Reutiliza el payload que ya validó `BearerAuthMiddleware`; si la ruta se
    invoca sin middleware (pruebas unitarias), vuelve a validar el token.
    """
    payload = getattr(request.state, "token_payload", None)
    if payload is None:
        try:
            payload = security.decode_token(token, expected_type="access")
        except security.TokenError as exc:
            raise credentials_exception from exc

    repo = UserRepository(session)
    user = await repo.get_by_id(payload.sub)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def client_credentials_from_request(request: Request) -> tuple[str | None, str | None]:
    """Credenciales de cliente desde `Authorization: Basic` (RFC 7617)."""
    return parse_basic_authorization(request.headers.get("Authorization")) or (None, None)


CurrentUser = Annotated[User, Depends(get_current_user)]


__all__ = [
    "CurrentUser",
    "client_credentials_from_request",
    "credentials_exception",
    "get_current_user",
    "oauth2_scheme",
]
