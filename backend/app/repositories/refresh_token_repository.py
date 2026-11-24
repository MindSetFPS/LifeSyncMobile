"""Repositorio de sesiones de refresh token (rotación y familias)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshTokenSession


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hash(self, token_hash: str) -> RefreshTokenSession | None:
        result = await self._session.execute(
            select(RefreshTokenSession).where(
                RefreshTokenSession.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        token_hash: str,
        family_id: str,
        user_id: str,
        client_id: str,
        scope: str,
        expires_at: datetime,
    ) -> RefreshTokenSession:
        session_token = RefreshTokenSession(
            token_hash=token_hash,
            family_id=family_id,
            user_id=user_id,
            client_id=client_id,
            scope=scope,
            expires_at=expires_at,
        )
        self._session.add(session_token)
        await self._session.flush()
        return session_token

    async def revoke(self, token: RefreshTokenSession, *, moment: datetime) -> None:
        token.revoked_at = moment
        await self._session.flush()

    async def revoke_family(self, family_id: str, *, moment: datetime) -> None:
        """Reutilización detectada: se revoca toda la cadena de rotación."""
        await self._session.execute(
            update(RefreshTokenSession)
            .where(
                RefreshTokenSession.family_id == family_id,
                RefreshTokenSession.revoked_at.is_(None),
            )
            .values(revoked_at=moment)
        )
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: str, *, moment: datetime) -> None:
        await self._session.execute(
            update(RefreshTokenSession)
            .where(
                RefreshTokenSession.user_id == user_id,
                RefreshTokenSession.revoked_at.is_(None),
            )
            .values(revoked_at=moment)
        )
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
