"""Flujo Authorization Code + PKCE (RFC 6749 §4.1, RFC 7636, RFC 8252).

Pensado para clientes nativos: el `code_verifier` nunca viaja por el
redirect y el código es de un solo uso, atado a `client_id` y `redirect_uri`.
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.oauth import OAuthError
from app.core.timeutils import aware_utc, utcnow
from app.models.authorization_code import AuthorizationCode
from app.models.oauth_client import OAuthClient
from app.models.user import User
from app.repositories.authorization_code_repository import AuthorizationCodeRepository


class AuthorizationCodeService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AuthorizationCodeRepository(session)
        self._session = session

    async def create(
        self,
        *,
        user: User,
        client: OAuthClient,
        redirect_uri: str,
        scope: str,
        code_challenge: str | None,
        code_challenge_method: str | None,
        nonce: str | None,
    ) -> str:
        """Emite un código opaco de un solo uso (solo se guarda su hash)."""
        if not code_challenge:
            raise OAuthError(
                "invalid_request", "PKCE es obligatorio para clientes públicos"
            )
        if code_challenge_method != "S256":
            raise OAuthError(
                "invalid_request", "Solo se admite code_challenge_method=S256"
            )
        if not 43 <= len(code_challenge) <= 128:
            raise OAuthError("invalid_request", "code_challenge con longitud inválida")

        raw_code = security.generate_token_handle()
        await self._repo.create(
            code_hash=security.sha256_hex(raw_code),
            user_id=user.id,
            client_id=client.client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
            expires_at=utcnow()
            + timedelta(seconds=settings.OAUTH_AUTHORIZATION_CODE_EXPIRE_SECONDS),
        )
        await self._repo.commit()
        return raw_code

    async def redeem(
        self,
        *,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> tuple[User, AuthorizationCode]:
        """Valida y consume el código; devuelve usuario y código usado."""
        stored = await self._repo.get_by_hash(security.sha256_hex(code))
        if stored is None:
            raise OAuthError("invalid_grant", "Código de autorización inválido")

        if stored.consumed_at is not None:
            raise OAuthError("invalid_grant", "El código ya fue utilizado")

        if aware_utc(stored.expires_at) <= aware_utc(utcnow()):
            raise OAuthError("invalid_grant", "El código expiró")

        if stored.client_id != client_id:
            raise OAuthError("invalid_grant", "El código pertenece a otro cliente")

        if stored.redirect_uri != redirect_uri:
            raise OAuthError("invalid_grant", "redirect_uri no coincide")

        if not stored.code_challenge or not security.verify_pkce(
            code_verifier, stored.code_challenge, stored.code_challenge_method or ""
        ):
            raise OAuthError("invalid_grant", "PKCE inválido")

        user = await self._session.get(User, stored.user_id)
        if user is None or not user.is_active:
            raise OAuthError("invalid_grant", "Usuario no encontrado o inactivo")

        await self._repo.consume(stored, moment=utcnow())
        await self._repo.commit()
        return user, stored


__all__ = ["AuthorizationCodeService"]
