"""Registro y autenticación de clientes OAuth 2.0 (RFC 6749 §2)."""

from __future__ import annotations

import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.oauth import OAuthError, parse_scope
from app.models.oauth_client import OAuthClient
from app.repositories.oauth_client_repository import OAuthClientRepository


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = OAuthClientRepository(session)

    async def get(self, client_id: str) -> OAuthClient | None:
        client = await self._repo.get_by_client_id(client_id)
        if client is None or not client.is_active:
            return None
        return client

    async def authenticate(
        self, client_id: str | None, client_secret: str | None
    ) -> OAuthClient:
        """Valida el cliente. Sin `client_id` se asume el cliente público móvil."""
        resolved_id = client_id or settings.OAUTH_SEED_CLIENT_ID
        client = await self.get(resolved_id)
        if client is None:
            raise OAuthError("invalid_client", "Cliente desconocido", status_code=401)

        if client.is_public:
            if client_secret:
                raise OAuthError(
                    "invalid_client",
                    "Un cliente público no debe presentar secreto",
                    status_code=401,
                )
            return client

        if not client.hashed_secret or not client_secret:
            raise OAuthError(
                "invalid_client", "Credenciales de cliente requeridas", status_code=401
            )
        if not security.verify_password(client_secret, client.hashed_secret):
            raise OAuthError("invalid_client", "Secreto de cliente inválido", status_code=401)
        return client

    def validate_redirect_uri(self, client: OAuthClient, redirect_uri: str) -> str:
        """Comparación exacta contra los URIs registrados (evita open redirect)."""
        allowed = client.redirect_uri_list
        if not redirect_uri:
            if len(allowed) == 1:
                return allowed[0]
            raise OAuthError("invalid_request", "redirect_uri requerido")
        if redirect_uri not in allowed:
            raise OAuthError("invalid_request", "redirect_uri no registrado")
        return redirect_uri

    def resolve_scope(
        self,
        client: OAuthClient,
        requested: str | None,
        *,
        default: str | None = None,
    ) -> str:
        """Limita los scopes pedidos a los autorizados para el cliente.

        `default` se usa cuando el cliente no solicita scopes; pasa por la misma
        validación que una petición explícita (sin escalada de privilegios).
        """
        allowed = set(client.scope_list)
        requested_scopes = parse_scope(requested) or parse_scope(
            default or settings.OAUTH_DEFAULT_SCOPE
        )
        rejected = [scope for scope in requested_scopes if scope not in allowed]
        if rejected:
            raise OAuthError(
                "invalid_scope",
                f"El cliente no puede solicitar: {', '.join(rejected)}",
            )
        return " ".join(requested_scopes)

    async def register_client(
        self,
        *,
        client_id: str,
        client_name: str,
        redirect_uris: list[str],
        allowed_scopes: str,
        is_public: bool = True,
    ) -> tuple[OAuthClient, str | None]:
        """Alta de cliente. Devuelve el secreto en claro solo en esta llamada."""
        if await self._repo.get_by_client_id(client_id) is not None:
            raise ValueError(f"El cliente {client_id!r} ya existe")

        raw_secret = None if is_public else secrets.token_urlsafe(32)
        hashed = security.hash_password(raw_secret) if raw_secret else None
        client = await self._repo.create(
            client_id=client_id,
            client_name=client_name,
            hashed_secret=hashed,
            is_public=is_public,
            redirect_uris=redirect_uris,
            allowed_scopes=allowed_scopes,
        )
        return client, raw_secret
