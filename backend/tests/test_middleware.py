"""Pruebas del middleware global de autenticación Bearer."""

from __future__ import annotations

from fastapi.testclient import TestClient

REGISTER = "/api/v1/auth/register"
TOKEN = "/api/v1/auth/token"
PASSWORD = "SuperSegura123!"


def _tokens(client: TestClient) -> dict:
    client.post(
        REGISTER,
        json={
            "email": "middleware@lifesync.mx",
            "full_name": "Middleware Test",
            "password": PASSWORD,
        },
    )
    response = client.post(
        TOKEN, data={"username": "middleware@lifesync.mx", "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_missing_token_is_rejected_by_middleware(client: TestClient) -> None:
    response = client.get("/api/v1/allergies")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["detail"] == "No se pudieron validar las credenciales"


def test_garbage_token_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/v1/allergies", headers={"Authorization": "Bearer no-es-un-jwt"}
    )
    assert response.status_code == 401


def test_refresh_token_is_not_accepted_as_access(client: TestClient) -> None:
    tokens = _tokens(client)
    response = client.get(
        "/api/v1/allergies",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert response.status_code == 401


def test_valid_access_token_reaches_route(client: TestClient) -> None:
    tokens = _tokens(client)
    response = client.get(
        "/api/v1/allergies",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200


def test_public_endpoints_do_not_require_bearer(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert (
        client.get("/.well-known/jwks.json").status_code == 200
    )
    assert (
        client.post(
            TOKEN,
            data={"username": "nadie@lifesync.mx", "password": "incorrecta"},
        ).status_code
        == 401
    )
