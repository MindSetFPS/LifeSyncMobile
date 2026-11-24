"""Configuración centralizada de la API.

Todas las variables de entorno se leen una sola vez a través de la instancia
`settings`. El patrón Singleton se aplica aquí y en la conexión a base de datos
para garantizar un único punto de configuración en todo el proceso.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuración centralizados (sobrescribibles por entorno)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "LifeSync Mobile API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite+aiosqlite:///./lifesync.db"

    # Criptografía asimétrica: par de llaves RSA para firmar/verificar JWT (RS256).
    JWT_PRIVATE_KEY_PATH: Path = Path("keys/private_key.pem")
    JWT_PUBLIC_KEY_PATH: Path = Path("keys/public_key.pem")
    JWT_ALGORITHM: str = "RS256"
    JWT_KEY_ID: str = "lifesync-rs256-1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Parámetros de hashing de contraseñas (nunca se guarda texto plano).
    BCRYPT_ROUNDS: int = 12

    # OAuth 2.0 / OpenID metadata
    OAUTH_ISSUER: str = "http://localhost:8000"
    OAUTH_TOKEN_URL: str = "/api/v1/auth/token"
    OAUTH_AUTHORIZE_URL: str = "/api/v1/oauth/authorize"
    OAUTH_SUPPORTED_SCOPES: str = "read write offline_access"
    OAUTH_DEFAULT_SCOPE: str = "read write"
    OAUTH_AUTHORIZATION_CODE_EXPIRE_SECONDS: int = 60

    # Registro de clientes OAuth (identificador público del cliente móvil).
    OAUTH_SEED_CLIENT_ID: str = "lifesync-android"
    OAUTH_SEED_CLIENT_REDIRECT_URIS: str = "com.lifesync.mobile://oauth2callback"

    # Exportación del historial clínico de emergencia.
    HEALTH_EXPORT_TTL_MINUTES: int = 60


@lru_cache
def get_settings() -> Settings:
    """Única instancia de Settings (Singleton) reutilizable en toda la app."""
    return Settings()


settings = get_settings()
