"""Pruebas de la capa OAuth 2.0 extendida.

Cubre: metadatos de descubrimiento, JWKS verificable, registro y autenticación
de clientes, Authorization Code + PKCE, rotación de refresh tokens con
detección de reutilización, revocación (RFC 7009) e introspección (RFC 7662).
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import re

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core import security
from app.core.database import database
from app.services.client_service import ClientService

REGISTER = "/api/v1/auth/register"
TOKEN = "/api/v1/auth/token"
REFRESH = "/api/v1/auth/refresh"
REVOKE = "/api/v1/auth/revoke"
INTROSPECT = "/api/v1/auth/introspect"
AUTHORIZE = "/api/v1/oauth/authorize"
REDIRECT_URI = "com.lifesync.mobile://oauth2callback"
CLIENT_ID = "lifesync-android"
PASSWORD = "SuperSegura123!"


def _pkce_verifier() -> tuple[str, str]:
    verifier = "v" * 50
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def _register_user(client: TestClient, email: str = "ana@lifesync.mx") -> None:
    response = client.post(
        REGISTER,
        json={"email": email, "full_name": "Ana Pérez", "password": PASSWORD},
    )
    assert response.status_code == 201, response.text


def _login(client: TestClient, email: str = "ana@lifesync.mx") -> dict:
    response = client.post(TOKEN, data={"username": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()


def _extract_flow_state(html: str) -> str:
    match = re.search(r'name="flow_state" value="([^"]+)"', html)
    assert match is not None, html
    return match.group(1)


def _authorize_and_approve(
    client: TestClient, *, challenge: str, scope: str = "read write offline_access"
) -> str:
    page = client.get(
        AUTHORIZE,
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": scope,
            "state": "estado-123",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    assert page.status_code == 200, page.text
    flow_state = _extract_flow_state(page.text)

    decision = client.post(
        AUTHORIZE,
        data={
            "flow_state": flow_state,
            "decision": "allow",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
        },
        follow_redirects=False,
    )
    assert decision.status_code == 302, decision.text
    return decision.headers["location"]


def _code_from_location(location: str) -> str:
    assert "error" not in location, location
    assert "state=estado-123" in location, location
    match = re.search(r"[?&]code=([^&]+)", location)
    assert match is not None, location
    return match.group(1)


# --------------------------------------------------------------------------- #
# Descubrimiento y JWKS
# --------------------------------------------------------------------------- #


def test_authorization_server_metadata_is_published(client: TestClient) -> None:
    body = client.get("/.well-known/oauth-authorization-server").json()

    assert body["issuer"]
    assert body["authorization_endpoint"].endswith("/api/v1/oauth/authorize")
    assert body["token_endpoint"].endswith("/api/v1/auth/token")
    assert body["revocation_endpoint"].endswith("/api/v1/auth/revoke")
    assert body["introspection_endpoint"].endswith("/api/v1/auth/introspect")
    assert body["jwks_uri"].endswith("/.well-known/jwks.json")
    assert "authorization_code" in body["grant_types_supported"]
    assert body["code_challenge_methods_supported"] == ["S256"]


def test_openid_configuration_matches_oauth_metadata(client: TestClient) -> None:
    oauth = client.get("/.well-known/oauth-authorization-server").json()
    oidc = client.get("/.well-known/openid-configuration").json()
    assert oidc == oauth


def test_jwks_verifies_issued_tokens(client: TestClient) -> None:
    _register_user(client)
    token = _login(client)["access_token"]

    key = client.get("/.well-known/jwks.json").json()["keys"][0]
    assert key["kty"] == "RSA"
    assert key["use"] == "sig"
    assert key["alg"] == "RS256"
    assert "*" not in key["n"]

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    claims = jwt.decode(token, public_key, algorithms=["RS256"])
    assert claims["type"] == "access"
    assert claims["iss"]


def test_jwks_does_not_leak_private_material(client: TestClient) -> None:
    body = client.get("/.well-known/jwks.json").text
    assert "PRIVATE" not in body
    key = client.get("/.well-known/jwks.json").json()["keys"][0]
    # Solo campos públicos de una JWK RSA (RFC 7517 §6.3.1).
    assert set(key) == {"kty", "use", "alg", "kid", "n", "e"}


def test_access_token_advertises_kid(client: TestClient) -> None:
    _register_user(client)
    header = jwt.get_unverified_header(_login(client)["access_token"])
    assert header["kid"] == "lifesync-rs256-1"


# --------------------------------------------------------------------------- #
# Clientes
# --------------------------------------------------------------------------- #


def test_unauthenticated_request_uses_seeded_public_client(client: TestClient) -> None:
    _register_user(client)
    body = _login(client)
    assert body["token_type"] == "bearer"
    assert body["scope"] == "read write offline_access"


def test_unknown_client_is_rejected(client: TestClient) -> None:
    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "client_id": "cliente-inexistente",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_client"


def test_confidential_client_requires_correct_secret(client: TestClient) -> None:
    _register_user(client)

    async def create_confidential() -> str:
        async with database.session_factory() as session:
            service = ClientService(session)
            _, secret = await service.register_client(
                client_id="lifesync-web",
                client_name="LifeSync Web",
                redirect_uris=["https://app.lifesync.mx/callback"],
                allowed_scopes="read",
                is_public=False,
            )
            await session.commit()
            assert secret is not None
            return secret

    secret = asyncio.run(create_confidential())

    wrong = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "client_id": "lifesync-web",
            "client_secret": "incorrecto",
        },
    )
    assert wrong.status_code == 401
    assert wrong.json()["error"] == "invalid_client"

    ok = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "client_id": "lifesync-web",
            "client_secret": secret,
            "scope": "read",
        },
    )
    assert ok.status_code == 200
    assert ok.json()["scope"] == "read"


def test_confidential_client_accepts_http_basic(client: TestClient) -> None:
    _register_user(client)

    async def create_confidential() -> str:
        async with database.session_factory() as session:
            service = ClientService(session)
            _, secret = await service.register_client(
                client_id="lifesync-basic",
                client_name="LifeSync Basic",
                redirect_uris=["https://app.lifesync.mx/callback"],
                allowed_scopes="read",
                is_public=False,
            )
            await session.commit()
            return secret or ""

    secret = asyncio.run(create_confidential())
    credentials = base64.b64encode(
        f"lifesync-basic:{secret}".encode("utf-8")
    ).decode("ascii")

    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "scope": "read",
        },
        headers={"Authorization": f"Basic {credentials}"},
    )
    assert response.status_code == 200
    assert response.json()["scope"] == "read"


def test_scope_outside_client_allowlist_is_rejected(client: TestClient) -> None:
    _register_user(client)
    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "scope": "admin",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_scope"


# --------------------------------------------------------------------------- #
# Authorization Code + PKCE
# --------------------------------------------------------------------------- #


def test_authorize_requires_pkce(client: TestClient) -> None:
    _register_user(client)
    response = client.get(
        AUTHORIZE,
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "error=invalid_request" in response.headers["location"]


def test_authorize_rejects_unregistered_redirect_uri(client: TestClient) -> None:
    response = client.get(
        AUTHORIZE,
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": "https://evil.example/callback",
            "code_challenge": "c" * 43,
            "code_challenge_method": "S256",
        },
    )
    assert response.status_code == 400
    assert "redirect_uri" in response.text


def test_authorization_code_flow_issues_tokens(client: TestClient) -> None:
    _register_user(client)
    verifier, challenge = _pkce_verifier()
    location = _authorize_and_approve(client, challenge=challenge)

    code = _code_from_location(location)
    response = client.post(
        TOKEN,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
            "client_id": CLIENT_ID,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["scope"] == "read write offline_access"

    claims = security.decode_token(body["access_token"])
    assert claims.client_id == CLIENT_ID
    assert claims.scope == "read write offline_access"


def test_authorization_code_is_single_use(client: TestClient) -> None:
    _register_user(client)
    verifier, challenge = _pkce_verifier()
    code = _code_from_location(_authorize_and_approve(client, challenge=challenge))

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
        "client_id": CLIENT_ID,
    }
    assert client.post(TOKEN, data=payload).status_code == 200

    replay = client.post(TOKEN, data=payload)
    assert replay.status_code == 400
    assert replay.json()["error"] == "invalid_grant"


def test_authorization_code_rejects_wrong_pkce_verifier(client: TestClient) -> None:
    _register_user(client)
    _, challenge = _pkce_verifier()
    code = _code_from_location(_authorize_and_approve(client, challenge=challenge))

    response = client.post(
        TOKEN,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": "x" * 50,
            "client_id": CLIENT_ID,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"


def test_authorization_code_rejects_redirect_mismatch(client: TestClient) -> None:
    _register_user(client)
    verifier, challenge = _pkce_verifier()
    code = _code_from_location(_authorize_and_approve(client, challenge=challenge))

    response = client.post(
        TOKEN,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "com.lifesync.mobile://otro",
            "code_verifier": verifier,
            "client_id": CLIENT_ID,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_grant"


def test_denied_consent_returns_access_denied(client: TestClient) -> None:
    _register_user(client)
    _, challenge = _pkce_verifier()
    page = client.get(
        AUTHORIZE,
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "state": "estado-123",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    flow_state = _extract_flow_state(page.text)

    decision = client.post(
        AUTHORIZE,
        data={"flow_state": flow_state, "decision": "deny"},
        follow_redirects=False,
    )
    assert decision.status_code == 302
    assert "error=access_denied" in decision.headers["location"]
    assert "state=estado-123" in decision.headers["location"]


def test_wrong_password_keeps_consent_page(client: TestClient) -> None:
    _register_user(client)
    _, challenge = _pkce_verifier()
    page = client.get(
        AUTHORIZE,
        params={
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        },
    )
    flow_state = _extract_flow_state(page.text)

    decision = client.post(
        AUTHORIZE,
        data={
            "flow_state": flow_state,
            "decision": "allow",
            "username": "ana@lifesync.mx",
            "password": "incorrecta",
        },
        follow_redirects=False,
    )
    assert decision.status_code == 200
    assert "Correo o contraseña incorrectos" in decision.text


# --------------------------------------------------------------------------- #
# Rotación, revocación e introspección
# --------------------------------------------------------------------------- #


def test_refresh_token_rotation_and_reuse_detection(client: TestClient) -> None:
    _register_user(client)
    first = _login(client)["refresh_token"]

    rotated = client.post(TOKEN, data={"grant_type": "refresh_token", "refresh_token": first})
    assert rotated.status_code == 200
    second = rotated.json()["refresh_token"]
    assert second != first

    reuse = client.post(TOKEN, data={"grant_type": "refresh_token", "refresh_token": first})
    assert reuse.status_code == 400
    assert reuse.json()["error"] == "invalid_grant"

    # La familia completa queda revocada: el token vigente también se invalida.
    after = client.post(TOKEN, data={"grant_type": "refresh_token", "refresh_token": second})
    assert after.status_code == 400


def test_refresh_tokens_are_not_persisted_in_clear(client: TestClient) -> None:
    _register_user(client)
    refresh_token = _login(client)["refresh_token"]

    from sqlalchemy import select

    from app.models.refresh_token import RefreshTokenSession

    async def stored_hashes() -> list[str]:
        async with database.session_factory() as session:
            result = await session.execute(select(RefreshTokenSession))
            return [row.token_hash for row in result.scalars().all()]

    hashes = asyncio.run(stored_hashes())
    assert refresh_token not in hashes
    assert security.sha256_hex(refresh_token) in hashes


def test_revocation_invalidates_refresh_token(client: TestClient) -> None:
    _register_user(client)
    refresh_token = _login(client)["refresh_token"]

    revoked = client.post(REVOKE, data={"token": refresh_token})
    assert revoked.status_code == 200
    assert revoked.json() == {}

    response = client.post(
        TOKEN, data={"grant_type": "refresh_token", "refresh_token": refresh_token}
    )
    assert response.status_code == 400


def test_revocation_of_unknown_token_still_returns_200(client: TestClient) -> None:
    assert client.post(REVOKE, data={"token": "no-existe"}).status_code == 200


def test_introspection_reports_active_access_token(client: TestClient) -> None:
    _register_user(client)
    access = _login(client)["access_token"]

    response = client.post(INTROSPECT, data={"token": access})
    assert response.status_code == 200
    body = response.json()
    assert body["active"] is True
    assert body["token_type"] == "Bearer"
    assert body["scope"] == "read write offline_access"
    assert body["client_id"] == CLIENT_ID


def test_introspection_reports_inactive_for_garbage(client: TestClient) -> None:
    response = client.post(INTROSPECT, data={"token": "no-es-un-token"})
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_unsupported_grant_type_is_reported(client: TestClient) -> None:
    response = client.post(TOKEN, data={"grant_type": "implicit"})
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_grant_type"


def test_error_response_is_not_cacheable(client: TestClient) -> None:
    response = client.post(TOKEN, data={"grant_type": "implicit"})
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"


def test_me_works_with_authorization_code_token(client: TestClient) -> None:
    _register_user(client)
    verifier, challenge = _pkce_verifier()
    code = _code_from_location(_authorize_and_approve(client, challenge=challenge))

    tokens = client.post(
        TOKEN,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
            "client_id": CLIENT_ID,
        },
    ).json()

    profile = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert profile.status_code == 200
    assert profile.json()["email"] == "ana@lifesync.mx"


@pytest.mark.parametrize("scope", ["read", "write", "read write offline_access"])
def test_password_grant_honours_requested_scope(client: TestClient, scope: str) -> None:
    _register_user(client)
    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "scope": scope,
        },
    )
    assert response.status_code == 200
    assert response.json()["scope"] == scope


def test_password_grant_without_offline_access_issues_no_refresh(client: TestClient) -> None:
    _register_user(client)
    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "scope": "read write",
        },
    )
    assert response.status_code == 200
    assert response.json()["refresh_token"] is None


def test_default_scope_cannot_escalate_beyond_client_allowlist(client: TestClient) -> None:
    """Un cliente limitado a `read` no obtiene `offline_access` por omisión."""
    _register_user(client)

    async def create_read_only() -> str:
        async with database.session_factory() as session:
            service = ClientService(session)
            _, secret = await service.register_client(
                client_id="lifesync-readonly",
                client_name="LifeSync Read Only",
                redirect_uris=["https://app.lifesync.mx/callback"],
                allowed_scopes="read",
                is_public=False,
            )
            await session.commit()
            return secret or ""

    secret = asyncio.run(create_read_only())

    response = client.post(
        TOKEN,
        data={
            "grant_type": "password",
            "username": "ana@lifesync.mx",
            "password": PASSWORD,
            "client_id": "lifesync-readonly",
            "client_secret": secret,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_scope"
