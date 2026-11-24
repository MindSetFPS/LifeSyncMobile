"""Endpoint de autorización (RFC 6749 §4.1.1, Authorization Code + PKCE).

El recurso protegido vive en una app nativa, no en un navegador: el endpoint
presenta una página de consentimiento servida por el backend donde el usuario
inicia sesión. El redirect final es un deep link
(`com.lifesync.mobile://oauth2callback`) con `code` y `state`.

El estado del flujo (`client_id`, `redirect_uri`, `scope`, PKCE, `state`) se
firma como JWT y viaja en una cookie HttpOnly: el POST no confía en parámetros
reenviados por el navegador, lo que evita CSRF y manipulación del redirect.
"""

from __future__ import annotations

import html
from datetime import timedelta
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.database import get_db
from app.core.oauth import OAuthError, parse_scope
from app.services.auth_service import AuthService, InvalidCredentials
from app.services.authorization_code_service import AuthorizationCodeService
from app.services.client_service import ClientService

router = APIRouter(prefix="/oauth", tags=["oauth"])

_STATE_COOKIE = "lifesync_oauth_flow"
_STATE_PATH = "/api/v1/oauth"


def _flow_state(*, client_id: str, redirect_uri: str, scope: str, **extra: str) -> str:
    """Firma el estado pendiente del flujo (10 min) para la cookie HttpOnly."""
    claims = {
        "type": "oauth_flow",
        "pending": {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            **{key: value for key, value in extra.items() if value},
        },
    }
    return security.create_access_token(
        client_id, scope="", extra_claims=claims, expires_delta=timedelta(minutes=10)
    )


def _pending_from_cookie(request: Request) -> dict[str, str] | None:
    cookie = request.cookies.get(_STATE_COOKIE)
    if not cookie:
        return None
    try:
        claims = security.decode_token_claims(cookie, expected_type="oauth_flow")
    except security.TokenError:
        return None
    pending = claims.get("pending")
    if not isinstance(pending, dict):
        return None
    return {str(key): str(value) for key, value in pending.items()}


def _redirect(uri: str, params: dict[str, str]) -> RedirectResponse:
    separator = "&" if "?" in uri else "?"
    return RedirectResponse(f"{uri}{separator}{urlencode(params)}", status_code=302)


def _error_page(message: str, status_code: int = 400) -> HTMLResponse:
    """Error no redirigible: nunca se redirige a un `redirect_uri` no confiable."""
    body = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Solicitud inválida</title></head>
<body style="font-family:system-ui;padding:2rem">
<h1>Solicitud inválida</h1><p>{html.escape(message)}</p>
<p>Vuelve a la aplicación LifeSync Mobile para reintentar.</p>
</body></html>"""
    return HTMLResponse(body, status_code=status_code)


def _consent_page(
    *, client_name: str, scopes: list[str], flow_state: str, error: str | None
) -> HTMLResponse:
    scope_items = "".join(f"<li><code>{html.escape(scope)}</code></li>" for scope in scopes)
    error_html = (
        f'<p role="alert" style="color:#b00020">{html.escape(error)}</p>' if error else ""
    )
    body = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Autorizar {html.escape(client_name)}</title></head>
<body style="font-family:system-ui;max-width:24rem;margin:3rem auto;padding:0 1rem">
<h1 style="font-size:1.3rem">Autorizar {html.escape(client_name)}</h1>
<p>Esta aplicación solicita acceso a tu historial clínico de emergencia:</p>
<ul>{scope_items}</ul>
{error_html}
<form method="post" action="{_STATE_PATH}/authorize">
  <input type="hidden" name="flow_state" value="{html.escape(flow_state)}">
  <label>Correo<br><input type="email" name="username" autocomplete="username" required></label>
  <p><label>Contraseña<br><input type="password" name="password" autocomplete="current-password" required></label></p>
  <p><button type="submit" name="decision" value="allow">Autorizar</button>
     <button type="submit" name="decision" value="deny">Cancelar</button></p>
</form>
</body></html>"""
    return HTMLResponse(body)


@router.get(
    "/authorize",
    response_model=None,
    summary="Inicia el flujo Authorization Code + PKCE",
)
async def authorize(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    response_type: str | None = None,
    client_id: str | None = None,
    redirect_uri: str | None = None,
    scope: str | None = None,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
    nonce: str | None = None,
) -> HTMLResponse | RedirectResponse:
    """Valida la petición y muestra la página de consentimiento."""
    if not client_id:
        return _error_page("Falta el parámetro client_id")

    clients = ClientService(session)
    client = await clients.get(client_id)
    if client is None:
        return _error_page("Cliente desconocido")

    try:
        resolved_redirect = clients.validate_redirect_uri(client, redirect_uri or "")
        resolved_scope = clients.resolve_scope(client, scope)
    except OAuthError as exc:
        return _error_page(exc.description or exc.error)

    state_params = {"state": state} if state else {}

    if response_type != "code":
        return _redirect(
            resolved_redirect,
            {
                "error": "unsupported_response_type",
                "error_description": "Solo se admite response_type=code",
                **state_params,
            },
        )

    if not code_challenge or code_challenge_method != "S256":
        return _redirect(
            resolved_redirect,
            {
                "error": "invalid_request",
                "error_description": "PKCE con S256 es obligatorio",
                **state_params,
            },
        )

    flow_state = _flow_state(
        client_id=client.client_id,
        redirect_uri=resolved_redirect,
        scope=resolved_scope,
        state=state or "",
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        nonce=nonce or "",
    )

    result = _consent_page(
        client_name=client.client_name,
        scopes=parse_scope(resolved_scope),
        flow_state=flow_state,
        error=None,
    )
    result.set_cookie(
        _STATE_COOKIE,
        flow_state,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
        path=_STATE_PATH,
    )
    return result


@router.post(
    "/authorize",
    response_model=None,
    summary="Resuelve el consentimiento y emite el código",
)
async def authorize_decision(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    flow_state: Annotated[str | None, Form()] = None,
    decision: Annotated[str | None, Form()] = None,
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
) -> HTMLResponse | RedirectResponse:
    """Autentica al usuario y redirige con `code` o `error` (RFC 6749 §4.1.2)."""
    pending = _pending_from_cookie(request)
    if pending is None or not flow_state:
        return _error_page("Flujo de autorización expirado, reintenta desde la app")

    if request.cookies.get(_STATE_COOKIE) != flow_state:
        return _error_page("El estado del flujo no coincide (posible CSRF)")

    redirect_uri = pending.get("redirect_uri", "")
    state = pending.get("state", "")
    state_params = {"state": state} if state else {}

    if not redirect_uri:
        return _error_page("Flujo de autorización inválido")

    if decision != "allow":
        return _redirect(
            redirect_uri,
            {
                "error": "access_denied",
                "error_description": "El usuario canceló la autorización",
                **state_params,
            },
        )

    clients = ClientService(session)
    client = await clients.get(pending.get("client_id", ""))
    if client is None:
        return _error_page("Cliente desconocido")

    service = AuthService(session)
    try:
        user = await service.authenticate(username or "", password or "")
    except InvalidCredentials:
        return _consent_page(
            client_name=client.client_name,
            scopes=parse_scope(pending.get("scope", "")),
            flow_state=flow_state,
            error="Correo o contraseña incorrectos",
        )

    codes = AuthorizationCodeService(session)
    code = await codes.create(
        user=user,
        client=client,
        redirect_uri=redirect_uri,
        scope=pending.get("scope", ""),
        code_challenge=pending.get("code_challenge"),
        code_challenge_method=pending.get("code_challenge_method"),
        nonce=pending.get("nonce"),
    )

    result = _redirect(redirect_uri, {"code": code, **state_params})
    result.delete_cookie(_STATE_COOKIE, path=_STATE_PATH)
    return result


__all__ = ["router"]
