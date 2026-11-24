"""Enumeraciones clínicas compartidas por modelos y esquemas.

Los valores coinciden con los nombres para que SQLite, SQLAlchemy y Pydantic
serialicen exactamente el mismo literal en base de datos y en la API.
"""

from __future__ import annotations

from enum import StrEnum


class BloodType(StrEnum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"


class RhFactor(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class AllergyCategory(StrEnum):
    MEDICATION = "MEDICATION"
    FOOD = "FOOD"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    INSECT = "INSECT"
    OTHER = "OTHER"


class AllergySeverity(StrEnum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    ANAPHYLAXIS = "ANAPHYLAXIS"
    UNKNOWN = "UNKNOWN"


class AllergyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    SUSPECTED = "SUSPECTED"


class DoseUnit(StrEnum):
    MG = "MG"
    ML = "ML"
    MCG = "MCG"
    G = "G"
    IU = "IU"
    DROPS = "DROPS"
    PUFFS = "PUFFS"
    TABLET = "TABLET"
    CAPSULE = "CAPSULE"
    OTHER = "OTHER"


class MedicationRoute(StrEnum):
    ORAL = "ORAL"
    IV = "IV"
    IM = "IM"
    TOPICAL = "TOPICAL"
    INHALED = "INHALED"
    SUBLINGUAL = "SUBLINGUAL"
    RECTAL = "RECTAL"
    OTHER = "OTHER"


class ExportFormat(StrEnum):
    JSON = "JSON"
    CSV = "CSV"


class ExportStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class ExportSection(StrEnum):
    PROFILE = "PROFILE"
    ALLERGIES = "ALLERGIES"
    MEDICATIONS = "MEDICATIONS"
    CONTACTS = "CONTACTS"
    ALERTS = "ALERTS"


class AlertType(StrEnum):
    MEDICATION_REMINDER = "MEDICATION_REMINDER"
    APPOINTMENT = "APPOINTMENT"
    ALLERGY_WARNING = "ALLERGY_WARNING"
    VITAL_ANOMALY = "VITAL_ANOMALY"
    EMERGENCY = "EMERGENCY"


class AlertSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertRelatedType(StrEnum):
    ALLERGY = "ALLERGY"
    MEDICATION = "MEDICATION"
    CONTACT = "CONTACT"
    EXPORT = "EXPORT"
    NONE = "NONE"


class AlertDelivery(StrEnum):
    LOCAL_NOTIFICATION = "LOCAL_NOTIFICATION"


__all__ = [
    "AlertDelivery",
    "AlertRelatedType",
    "AlertSeverity",
    "AlertType",
    "AllergyCategory",
    "AllergySeverity",
    "AllergyStatus",
    "BloodType",
    "DoseUnit",
    "ExportFormat",
    "ExportSection",
    "ExportStatus",
    "MedicationRoute",
    "RhFactor",
]
