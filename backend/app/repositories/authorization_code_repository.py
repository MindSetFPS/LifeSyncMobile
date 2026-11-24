"""Repositorio de códigos de autorización de un solo uso."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.authorization_code import AuthorizationCode


class AuthorizationCodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hash(self, code_hash: str) -> AuthorizationCode | None:
        result = await self._session.execute(
            select(AuthorizationCode).where(AuthorizationCode.code_hash == code_hash)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        code_hash: str,
        user_id: str,
        client_id: str,
        redirect_uri: str,
        scope: str,
        code_challenge: str | None,
        code_challenge_method: str | None,
        nonce: str | None,
        expires_at: datetime,
    ) -> AuthorizationCode:
        code = AuthorizationCode(
            code_hash=code_hash,
            user_id=user_id,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
            expires_at=expires_at,
        )
        self._session.add(code)
        await self._session.flush()
        return code

    async def consume(self, code: AuthorizationCode, *, moment: datetime) -> None:
        code.consumed_at = moment
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
