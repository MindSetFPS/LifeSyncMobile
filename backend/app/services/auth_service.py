"""Servicio de autenticación: orquesta repositorio, hashing y JWT."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate


class EmailAlreadyExists(Exception):
    """El correo ya está registrado."""


class InvalidCredentials(Exception):
    """Credenciales inválidas (mensaje genérico para no filtrar información)."""


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

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

    @staticmethod
    def issue_tokens(user: User) -> Token:
        return Token(
            access_token=security.create_access_token(subject=user.id),
            refresh_token=security.create_refresh_token(subject=user.id),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> Token:
        try:
            payload = security.decode_token(refresh_token, expected_type="refresh")
        except security.TokenError as exc:
            raise InvalidCredentials("Refresh token inválido") from exc
        user = await self._repo.get_by_id(payload.sub)
        if user is None or not user.is_active:
            raise InvalidCredentials("Usuario no encontrado o inactivo")
        return self.issue_tokens(user)
