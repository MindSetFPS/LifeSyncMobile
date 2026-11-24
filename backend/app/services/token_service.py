"""Emisión, rotación, revocación e introspección de tokens OAuth 2.0.

Refresh tokens son opacos (no JWT) y se persisten hasheados con SHA-256. Cada
canje rota el token dentro de la misma familia; presentar un token ya rotado
revoca la familia completa (RFC 6819 §5.2.2.3).
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.oauth import OAuthError
from app.core.timeutils import aware_utc, utcnow
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.oauth import TokenResponse


def _looks_like_jwt(token: str) -> bool:
    """Los refresh tokens son opacos; un JWS tiene exactamente tres segmentos."""
    return token.count(".") == 2


class TokenService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = RefreshTokenRepository(session)

    def _access_token(self, user: User, client_id: str, scope: str) -> str:
        return security.create_access_token(
            user.id, scope=scope, client_id=client_id
        )

    async def issue(
        self,
        user: User,
        *,
        client_id: str,
        scope: str,
        family_id: str | None = None,
        include_refresh: bool = True,
    ) -> TokenResponse:
        """Emite un par de tokens y persiste la sesión de refresh."""
        access_token = self._access_token(user, client_id, scope)
        refresh_raw: str | None = None

        if include_refresh:
            refresh_raw = security.generate_token_handle()
            await self._repo.create(
                token_hash=security.sha256_hex(refresh_raw),
                family_id=family_id or str(uuid.uuid4()),
                user_id=user.id,
                client_id=client_id,
                scope=scope,
                expires_at=utcnow()
                + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            await self._repo.commit()

        return TokenResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_raw,
            scope=scope,
        )

    async def rotate(self, refresh_token: str, *, client_id: str | None) -> TokenResponse:
        """Canjea un refresh token una sola vez (grant_type=refresh_token)."""
        token_hash = security.sha256_hex(refresh_token)
        stored = await self._repo.get_by_hash(token_hash)
        if stored is None:
            # Un JWT (p. ej. un access token) presentado como refresh es uso
            # indebido del token: se señala como credencial inválida (401), no
            # como error de protocolo.
            if _looks_like_jwt(refresh_token):
                raise OAuthError(
                    "invalid_grant",
                    "El token no es un refresh token válido",
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise OAuthError("invalid_grant", "Refresh token desconocido")

        if stored.revoked_at is not None:
            raise OAuthError("invalid_grant", "Refresh token revocado")

        if stored.rotated_at is not None:
            await self._repo.revoke_family(stored.family_id, moment=utcnow())
            await self._repo.commit()
            raise OAuthError(
                "invalid_grant", "Reutilización detectada: sesión revocada"
            )

        if client_id and stored.client_id != client_id:
            raise OAuthError("invalid_grant", "El token pertenece a otro cliente")

        if aware_utc(stored.expires_at) <= aware_utc(utcnow()):
            raise OAuthError("invalid_grant", "Refresh token expirado")

        user = await self._session.get(User, stored.user_id)
        if user is None or not user.is_active:
            raise OAuthError("invalid_grant", "Usuario no encontrado o inactivo")

        stored.rotated_at = utcnow()
        response = await self.issue(
            user,
            client_id=stored.client_id,
            scope=stored.scope or settings.OAUTH_DEFAULT_SCOPE,
            family_id=stored.family_id,
            include_refresh=True,
        )
        return response

    async def revoke(self, token: str, *, client_id: str | None) -> None:
        """RFC 7009: revoca refresh tokens; responde igual si no existe."""
        stored = await self._repo.get_by_hash(security.sha256_hex(token))
        if stored is None:
            return
        if client_id and stored.client_id != client_id:
            return
        await self._repo.revoke_family(stored.family_id, moment=utcnow())
        await self._repo.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self._repo.revoke_all_for_user(user_id, moment=utcnow())
        await self._repo.commit()

    def introspect(self, token: str) -> dict[str, object]:
        """RFC 7662: metadatos de un access token JWT verificado."""
        try:
            payload = security.decode_token(token, expected_type="access")
        except security.TokenError:
            return {"active": False}

        return {
            "active": True,
            "scope": payload.scope,
            "client_id": payload.client_id,
            "token_type": "Bearer",
            "exp": int(payload.exp.timestamp()),
            "iat": int(payload.iat.timestamp()),
            "sub": payload.sub,
            "iss": payload.iss,
            "jti": payload.jti,
        }


__all__ = ["TokenService"]
