"""Registro de metadatos ORM.

Importar este módulo garantiza que `Base.metadata` conoce todas las tablas
antes de `create_all()`.
"""

from app.models.authorization_code import AuthorizationCode
from app.models.base import Base
from app.models.oauth_client import OAuthClient
from app.models.refresh_token import RefreshTokenSession
from app.models.user import User

__all__ = ["AuthorizationCode", "Base", "OAuthClient", "RefreshTokenSession", "User"]
