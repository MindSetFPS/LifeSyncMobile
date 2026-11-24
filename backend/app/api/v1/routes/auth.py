"""Rutas de autenticación y endpoints OAuth 2.0.

* `/auth/register`, `/auth/me`: registro y perfil.
* `/auth/token`: endpoint de token con despacho de `grant_type`
  (`password` heredado de Sprint 1, `refresh_token`, `authorization_code`).
* `/auth/refresh`: compatibilidad con el cliente Sprint 1.
* `/auth/revoke` (RFC 7009) e `/auth/introspect` (RFC 7662).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CurrentUser, client_credentials_from_request
from app.core.config import settings
from app.core.database import get_db
from app.core.oauth import OAuthError, parse_scope
from app.schemas.auth import RefreshRequest, UserCreate, UserOut
from app.schemas.oauth import IntrospectionResponse, TokenResponse
from app.services.auth_service import AuthService, EmailAlreadyExists, InvalidCredentials
from app.services.authorization_code_service import AuthorizationCodeService
from app.services.client_service import ClientService
from app.services.token_service import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
async def register(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserOut:
    service = AuthService(session)
    try:
        return UserOut.model_validate(await service.register(payload))
    except EmailAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Endpoint de token OAuth 2.0",
)
async def token(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    grant_type: Annotated[str | None, Form()] = None,
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    scope: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    code: Annotated[str | None, Form()] = None,
    redirect_uri: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
) -> TokenResponse:
    """Emite tokens según el grant. Errores siguen RFC 6749 §5.2."""
    resolved_grant = grant_type or ("password" if username else "")
    if not resolved_grant:
        raise OAuthError("invalid_request", "grant_type es obligatorio")

    basic_id, basic_secret = client_credentials_from_request(request)
    effective_client_id = client_id or basic_id
    effective_secret = client_secret or basic_secret

    clients = ClientService(session)
    client = await clients.authenticate(effective_client_id, effective_secret)

    tokens = TokenService(session)

    if resolved_grant == "password":
        if not username or not password:
            raise OAuthError(
                "invalid_request", "username y password son obligatorios"
            )
        # Sin `scope` explícito se concede `offline_access` (contrato de Sprint 1)
        # y se valida igualmente contra los scopes autorizados del cliente.
        granted = clients.resolve_scope(
            client,
            scope,
            default=f"{settings.OAUTH_DEFAULT_SCOPE} offline_access",
        )
        service = AuthService(session)
        try:
            user = await service.authenticate(username, password)
        except InvalidCredentials:
            raise OAuthError(
                "invalid_grant",
                "Credenciales incorrectas",
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
            ) from None
        return await tokens.issue(
            user,
            client_id=client.client_id,
            scope=granted,
            include_refresh="offline_access" in parse_scope(granted),
        )

    if resolved_grant == "refresh_token":
        if not refresh_token:
            raise OAuthError("invalid_request", "refresh_token es obligatorio")
        return await tokens.rotate(refresh_token, client_id=client.client_id)

    if resolved_grant == "authorization_code":
        if not code or not redirect_uri or not code_verifier:
            raise OAuthError(
                "invalid_request",
                "code, redirect_uri y code_verifier son obligatorios",
            )
        codes = AuthorizationCodeService(session)
        user, stored = await codes.redeem(
            code=code,
            client_id=client.client_id,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
        return await tokens.issue(
            user,
            client_id=client.client_id,
            scope=stored.scope,
            include_refresh="offline_access" in parse_scope(stored.scope),
        )

    raise OAuthError("unsupported_grant_type", f"grant_type no soportado: {resolved_grant}")


@router.post("/refresh", response_model=TokenResponse, summary="Renovar access token")
async def refresh(
    payload: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Compatibilidad Sprint 1: misma rotación que `grant_type=refresh_token`."""
    tokens = TokenService(session)
    return await tokens.rotate(payload.refresh_token, client_id=None)


@router.post(
    "/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revocar un token (RFC 7009)",
)
async def revoke(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str | None, Form()] = None,
    token_type_hint: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> dict[str, str]:
    """Revoca la familia del refresh token. Siempre responde 200 (RFC 7009 §2.2)."""
    if not token:
        raise OAuthError("invalid_request", "token es obligatorio")

    basic_id, basic_secret = client_credentials_from_request(request)
    clients = ClientService(session)
    client = await clients.authenticate(
        client_id or basic_id, client_secret or basic_secret
    )
    await TokenService(session).revoke(token, client_id=client.client_id)
    return {}


@router.post(
    "/introspect",
    response_model=IntrospectionResponse,
    summary="Introspección de token (RFC 7662)",
)
async def introspect(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str | None, Form()] = None,
    token_type_hint: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> IntrospectionResponse:
    if not token:
        raise OAuthError("invalid_request", "token es obligatorio")

    basic_id, basic_secret = client_credentials_from_request(request)
    clients = ClientService(session)
    await clients.authenticate(client_id or basic_id, client_secret or basic_secret)
    data = TokenService(session).introspect(token)
    return IntrospectionResponse.model_validate(data)


@router.get("/me", response_model=UserOut, summary="Perfil del usuario autenticado")
async def read_me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)
