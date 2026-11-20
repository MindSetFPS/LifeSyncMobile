"""Primitivas criptográficas: hashing de contraseñas y JWT firmado con RS256.

* Las contraseñas NUNCA se almacenan en texto plano ni con cifrado simple:
  se usa bcrypt (hash saltado y adaptativo, irreversible).
* Los tokens JWT se firman con un par de llaves RSA (4096 bits). La firma
  asimétrica permite al cliente verificar con la llave pública sin exponer
  la privada, cumpliendo el flujo OAuth 2.0 / JWT.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings

_BCRYPT_MAX_BYTES = 72


class TokenError(Exception):
    """Error al validar un token JWT."""


@dataclass(frozen=True, slots=True)
class TokenPayload:
    """Payload verificado de un access token."""

    sub: str
    exp: datetime
    iat: datetime
    jti: str
    type: str
    scope: str = ""


def _prepare_password(password: str) -> bytes:
    """Pre-hash SHA-256 + base64 para evitar el límite de 72 bytes de bcrypt."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    """Devuelve un hash bcrypt saltado (nunca reversible)."""
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(_prepare_password(password), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comparación en tiempo constante contra el hash almacenado."""
    try:
        return bcrypt.checkpw(
            _prepare_password(plain_password), hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def ensure_rsa_keypair(
    private_path: Path | None = None, public_path: Path | None = None
) -> None:
    """Genera el par de llaves RSA si no existe (idempotente)."""
    private_path = private_path or settings.JWT_PRIVATE_KEY_PATH
    public_path = public_path or settings.JWT_PUBLIC_KEY_PATH
    if private_path.exists() and public_path.exists():
        return

    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _load_private_key() -> str:
    return settings.JWT_PRIVATE_KEY_PATH.read_text(encoding="utf-8")


def _load_public_key() -> str:
    return settings.JWT_PUBLIC_KEY_PATH.read_text(encoding="utf-8")


def create_access_token(
    subject: str,
    *,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Crea un access token JWT firmado (RS256)."""
    now = datetime.now(UTC)
    expire = now + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "scope": "read write",
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, _load_private_key(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str, *, expires_delta: timedelta | None = None
) -> str:
    """Crea un refresh token de larga duración, también firmado."""
    now = datetime.now(UTC)
    expire = now + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    claims = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
        "scope": "refresh",
    }
    return jwt.encode(claims, _load_private_key(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, *, expected_type: str = "access") -> TokenPayload:
    """Verifica firma, expiración y tipo; devuelve el payload tipado."""
    try:
        raw = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "sub", "jti"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Token inválido o expirado") from exc

    if raw.get("type") != expected_type:
        raise TokenError(f"Tipo de token inesperado: {raw.get('type')}")

    return TokenPayload(
        sub=str(raw["sub"]),
        exp=datetime.fromtimestamp(raw["exp"], tz=UTC),
        iat=datetime.fromtimestamp(raw["iat"], tz=UTC),
        jti=str(raw["jti"]),
        type=str(raw["type"]),
        scope=str(raw.get("scope", "")),
    )
