"""Servicio de autenticación: orquesta repositorio, hashing y emisión de tokens."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate
from app.schemas.oauth import TokenResponse
from app.services.token_service import TokenService


class EmailAlreadyExists(Exception):
    """El correo ya está registrado."""


class InvalidCredentials(Exception):
    """Credenciales inválidas (mensaje genérico para no filtrar información)."""


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)
        self._tokens = TokenService(session)

    async def register(self, data: UserCreate) -> User:
        if await self._repo.get_by_email(data.email):
            raise EmailAlreadyExists("El correo ya está registrado")
        return await self._repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=security.hash_password(data.password),
        )

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._repo.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidCredentials("Credenciales inválidas")
        if not security.verify_password(password, user.hashed_password):
            raise InvalidCredentials("Credenciales inválidas")
        return user

    async def issue_tokens(
        self, user: User, *, client_id: str, scope: str
    ) -> TokenResponse:
        return await self._tokens.issue(user, client_id=client_id, scope=scope)

    async def refresh(self, refresh_token: str, *, client_id: str | None) -> TokenResponse:
        return await self._tokens.rotate(refresh_token, client_id=client_id)


__all__ = ["AuthService", "EmailAlreadyExists", "InvalidCredentials"]
