"""Repositorio de clientes OAuth registrados."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oauth_client import OAuthClient


class OAuthClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_client_id(self, client_id: str) -> OAuthClient | None:
        result = await self._session.execute(
            select(OAuthClient).where(OAuthClient.client_id == client_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        client_id: str,
        client_name: str,
        hashed_secret: str | None,
        is_public: bool,
        redirect_uris: list[str],
        allowed_scopes: str,
    ) -> OAuthClient:
        client = OAuthClient(
            client_id=client_id,
            client_name=client_name,
            hashed_secret=hashed_secret,
            is_public=is_public,
            redirect_uris="\n".join(redirect_uris),
            allowed_scopes=allowed_scopes,
        )
        self._session.add(client)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(client)
        return client

    async def list_all(self) -> list[OAuthClient]:
        result = await self._session.execute(select(OAuthClient))
        return list(result.scalars().all())
