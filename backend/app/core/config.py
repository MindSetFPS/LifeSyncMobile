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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Parámetros de hashing de contraseñas (nunca se guarda texto plano).
    BCRYPT_ROUNDS: int = 12

    # OAuth 2.0
    OAUTH_TOKEN_URL: str = "/api/v1/auth/token"


@lru_cache
def get_settings() -> Settings:
    """Única instancia de Settings (Singleton) reutilizable en toda la app."""
    return Settings()


settings = get_settings()
