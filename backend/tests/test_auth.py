"""Pruebas del esquema de autenticación (Sprint 1).

Cubre: registro sin texto plano, duplicados, validación, OAuth 2.0 password
grant, firma RS256 verifiable, protección de rutas, refresh y manipulación.
"""

from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core import security
from app.core.config import settings
from app.core.database import database
from app.models.user import User
from app.schemas.auth import Token

REGISTER = "/api/v1/auth/register"
TOKEN = "/api/v1/auth/token"
ME = "/api/v1/auth/me"
REFRESH = "/api/v1/auth/refresh"


def _register(client: TestClient, email: str = "ana@lifesync.mx") -> dict:
    response = client.post(
        REGISTER,
        json={
            "email": email,
            "full_name": "Ana Pérez",
            "password": "SuperSegura123!",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _login(client: TestClient, email: str, password: str) -> dict:
    response = client.post(
        TOKEN, data={"username": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_register_does_not_leak_password(client: TestClient) -> None:
    body = _register(client)
    assert "password" not in body
    assert "hashed_password" not in body
    assert body["email"] == "ana@lifesync.mx"
    assert body["is_active"] is True


def test_password_is_stored_only_as_bcrypt_hash(client: TestClient) -> None:
    _register(client)
    import asyncio

    async def read_hash() -> str:
        async with database.session_factory() as session:
            result = await session.execute(select(User))
            user = result.scalar_one()
            return user.hashed_password

    stored = asyncio.run(read_hash())
    assert stored != "SuperSegura123!"
    assert stored.startswith("$2")  # prefijo bcrypt
    assert security.verify_password("SuperSegura123!", stored)
    assert not security.verify_password("incorrecta", stored)


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"email": "ana@lifesync.mx", "full_name": "Ana", "password": "corta"}, 422),
        ({"email": "no-es-correo", "full_name": "Ana", "password": "SuperSegura123!"}, 422),
    ],
)
def test_register_validates_payload(
    client: TestClient, payload: dict, expected_status: int
) -> None:
    assert client.post(REGISTER, json=payload).status_code == expected_status


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    _register(client)
    response = client.post(
        REGISTER,
        json={
            "email": "ana@lifesync.mx",
            "full_name": "Otra Ana",
            "password": "SuperSegura123!",
        },
    )
    assert response.status_code == 409


def test_login_returns_rs256_signed_tokens(client: TestClient) -> None:
    _register(client)
    data = _login(client, "ana@lifesync.mx", "SuperSegura123!")
    token = Token.model_validate(data)

    assert token.token_type == "bearer"
    assert token.expires_in == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    header = jwt.get_unverified_header(token.access_token)
    assert header["alg"] == "RS256"

    payload = security.decode_token(token.access_token)
    assert payload.sub
    assert payload.type == "access"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    _register(client)
    response = client.post(
        TOKEN, data={"username": "ana@lifesync.mx", "password": "mala"}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_requires_bearer_token(client: TestClient) -> None:
    assert client.get(ME).status_code == 401


def test_me_returns_profile_with_valid_token(client: TestClient) -> None:
    _register(client)
    token = Token.model_validate(_login(client, "ana@lifesync.mx", "SuperSegura123!"))
    response = client.get(ME, headers={"Authorization": f"Bearer {token.access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "ana@lifesync.mx"


def test_me_rejects_tampered_token(client: TestClient) -> None:
    _register(client)
    token = _login(client, "ana@lifesync.mx", "SuperSegura123!")["access_token"]
    tampered = token[:-3] + ("AAA" if not token.endswith("AAA") else "BBB")
    response = client.get(ME, headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == 401


def test_access_token_cannot_be_used_as_refresh(client: TestClient) -> None:
    _register(client)
    access = _login(client, "ana@lifesync.mx", "SuperSegura123!")["access_token"]
    response = client.post(REFRESH, json={"refresh_token": access})
    assert response.status_code == 401


def test_refresh_rotates_valid_tokens(client: TestClient) -> None:
    _register(client)
    first = Token.model_validate(_login(client, "ana@lifesync.mx", "SuperSegura123!"))
    response = client.post(REFRESH, json={"refresh_token": first.refresh_token})
    assert response.status_code == 200

    second = Token.model_validate(response.json())
    assert second.access_token != first.access_token
    assert security.decode_token(second.access_token).type == "access"


def test_expired_token_is_rejected(client: TestClient) -> None:
    from datetime import timedelta

    _register(client)
    expired = security.create_access_token(
        "some-id", expires_delta=timedelta(seconds=-1)
    )
    response = client.get(ME, headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
