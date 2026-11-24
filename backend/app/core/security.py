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
import hmac
import secrets
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
    client_id: str = ""
    iss: str = ""


def sha256_hex(value: str) -> str:
    """Hash SHA-256 en hexadecimal (códigos y tokens nunca se guardan en claro)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_pkce(
    code_verifier: str, code_challenge: str, method: str
) -> bool:
    """Verifica el valor PKCE según RFC 7636 §4.6."""
    if not 43 <= len(code_verifier) <= 128:
        return False
    if method == "S256":
        computed = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest())
            .rstrip(b"=")
            .decode("ascii")
        )
        return hmac.compare_digest(computed, code_challenge)
    return False


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


def _sign(claims: dict[str, Any]) -> str:
    """Firma el JWT exponiendo el `kid` para que JWKS resuelva la llave pública."""
    return jwt.encode(
        claims,
        _load_private_key(),
        algorithm=settings.JWT_ALGORITHM,
        headers={"kid": settings.JWT_KEY_ID, "typ": "JWT"},
    )


def create_access_token(
    subject: str,
    *,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
    scope: str | None = None,
    client_id: str | None = None,
    audience: str | None = None,
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
        "scope": scope or settings.OAUTH_DEFAULT_SCOPE,
        "iss": settings.OAUTH_ISSUER,
    }
    if client_id:
        claims["client_id"] = client_id
    if audience:
        claims["aud"] = audience
    if extra_claims:
        claims.update(extra_claims)
    return _sign(claims)


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
        "scope": "offline_access",
        "iss": settings.OAUTH_ISSUER,
    }
    return _sign(claims)


def decode_token(token: str, *, expected_type: str = "access") -> TokenPayload:
    """Verifica firma, expiración, emisor y tipo; devuelve el payload tipado."""
    raw = decode_token_claims(token, expected_type=expected_type)

    return TokenPayload(
        sub=str(raw["sub"]),
        exp=datetime.fromtimestamp(raw["exp"], tz=UTC),
        iat=datetime.fromtimestamp(raw["iat"], tz=UTC),
        jti=str(raw["jti"]),
        type=str(raw["type"]),
        scope=str(raw.get("scope", "")),
        client_id=str(raw.get("client_id", "")),
        iss=str(raw.get("iss", "")),
    )


def decode_token_claims(
    token: str, *, expected_type: str | None = None
) -> dict[str, Any]:
    """Verifica firma, expiración y emisor; devuelve los claims crudos.

    `expected_type=None` omite la comprobación del claim `type`, necesario para
    tokens internos (por ejemplo el estado firmado del flujo de autorización).
    """
    try:
        raw = jwt.decode(
            token,
            _load_public_key(),
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.OAUTH_ISSUER,
            options={
                "require": ["exp", "iat", "sub", "jti", "iss"],
                "verify_aud": False,
            },
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Token inválido o expirado") from exc

    if expected_type is not None and raw.get("type") != expected_type:
        raise TokenError(f"Tipo de token inesperado: {raw.get('type')}")

    return dict(raw)


def public_key_pem() -> str:
    """Llave pública PEM expuesta por JWKS (nunca la privada)."""
    return _load_public_key()


def generate_token_handle() -> str:
    """Identificador opaco e impredecible para códigos y refresh tokens."""
    return secrets.token_urlsafe(48)


__all__ = [
    "TokenError",
    "TokenPayload",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "ensure_rsa_keypair",
    "generate_token_handle",
    "hash_password",
    "public_key_pem",
    "sha256_hex",
    "verify_password",
    "verify_pkce",
]
