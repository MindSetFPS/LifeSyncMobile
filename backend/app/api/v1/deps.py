"""Dependencias de FastAPI para autenticación OAuth 2.0 (Bearer)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import InvalidCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.OAUTH_TOKEN_URL)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudieron validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Valida el JWT RS256 y devuelve el usuario autenticado."""
    try:
        payload = security.decode_token(token, expected_type="access")
    except security.TokenError as exc:
        raise credentials_exception from exc

    repo = UserRepository(session)
    user = await repo.get_by_id(payload.sub)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
