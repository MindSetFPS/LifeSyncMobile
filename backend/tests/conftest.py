"""Fixtures compartidas: llaves RSA temporales y base de datos aislada por test."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import database
from app.core.security import ensure_rsa_keypair


@pytest.fixture
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """App completa con DB SQLite temporal y par de llaves RSA efímero."""
    private = tmp_path / "private_key.pem"
    public = tmp_path / "public_key.pem"

    monkeypatch.setattr(settings, "JWT_PRIVATE_KEY_PATH", private)
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", public)
    monkeypatch.setattr(
        settings, "DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/lifesync_test.db"
    )

    database.reset()
    ensure_rsa_keypair(private, public)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    database.reset()
