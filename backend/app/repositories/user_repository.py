"""Repositorio de usuarios: único punto de acceso a la tabla `users`."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._session.get(User, user_id)

    async def create(
        self, *, email: str, full_name: str, hashed_password: str
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(user)
        return user
