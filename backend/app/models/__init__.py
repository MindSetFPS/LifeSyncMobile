"""Registro de metadatos ORM.

Importar este módulo garantiza que `Base.metadata` conoce todas las tablas
antes de `create_all()`.
"""

from app.models.allergy import Allergy
from app.models.authorization_code import AuthorizationCode
from app.models.base import Base
from app.models.emergency_contact import EmergencyContact
from app.models.emergency_export import EmergencyExport
from app.models.medical_alert import MedicalAlert
from app.models.medical_profile import MedicalProfile
from app.models.medication import Medication
from app.models.oauth_client import OAuthClient
from app.models.refresh_token import RefreshTokenSession
from app.models.user import User

__all__ = [
    "Allergy",
    "AuthorizationCode",
    "Base",
    "EmergencyContact",
    "EmergencyExport",
    "MedicalAlert",
    "MedicalProfile",
    "Medication",
    "OAuthClient",
    "RefreshTokenSession",
    "User",
]
