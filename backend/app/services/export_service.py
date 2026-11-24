"""Servicio de exportación del historial clínico de emergencia.

El snapshot se genera en el servidor (Strategy JSON/CSV), se acota al dueño del
token y expira tras un TTL corto. No se registra contenido clínico en logs.
"""

from __future__ import annotations

import hashlib
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.timeutils import utcnow
from app.models.allergy import Allergy
from app.models.emergency_contact import EmergencyContact
from app.models.emergency_export import EmergencyExport
from app.models.enums import ExportSection, ExportStatus
from app.models.medical_alert import MedicalAlert
from app.models.medical_profile import MedicalProfile
from app.models.medication import Medication
from app.models.user import User
from app.repositories.emergency_export_repository import EmergencyExportRepository
from app.repositories.health_repository import HealthRepository
from app.schemas.health import EmergencyExportCreate
from app.services.export_strategies import EXPORT_STRATEGIES


class ExportUnavailableError(Exception):
    """El snapshot no está disponible (revocado o incompleto)."""


class ExportExpiredError(Exception):
    """El snapshot expiró."""


def _mask(value: str | None) -> str | None:
    if value is None:
        return None
    return "***" if len(value) <= 2 else f"***{value[-2:]}"


def _iso(value: Any) -> Any:
    return value.isoformat() if hasattr(value, "isoformat") else value


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._exports = EmergencyExportRepository(session)
        self._profiles = HealthRepository(session, MedicalProfile)
        self._allergies = HealthRepository(session, Allergy)
        self._medications = HealthRepository(session, Medication)
        self._contacts = HealthRepository(session, EmergencyContact)
        self._alerts = HealthRepository(session, MedicalAlert)

    async def list_exports(
        self, user_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[EmergencyExport]:
        return await self._exports.list_for_user(
            user_id, limit=limit, offset=offset
        )

    async def get_export(self, user_id: str, export_id: str) -> EmergencyExport:
        export = await self._exports.get_for_user(user_id, export_id)
        if export is None:
            raise ExportUnavailableError("Exportación no encontrada")
        return export

    async def create_export(
        self, user: User, payload: EmergencyExportCreate
    ) -> EmergencyExport:
        strategy = EXPORT_STRATEGIES[payload.format]
        data, record_count = await self._build_payload(user, payload.sections)
        content = strategy.render(data)
        now = utcnow()
        export = EmergencyExport(
            user_id=user.id,
            format=payload.format,
            status=ExportStatus.READY,
            sections=[section.value for section in payload.sections],
            strategy=strategy.name,
            strategy_version=strategy.version,
            requested_at=now,
            generated_at=now,
            expires_at=now + timedelta(minutes=settings.HEALTH_EXPORT_TTL_MINUTES),
            content_sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            record_count=record_count,
            content=content.decode("utf-8"),
        )
        return await self._exports.save(export)

    async def download(
        self, user_id: str, export_id: str
    ) -> tuple[EmergencyExport, bytes]:
        export = await self.get_export(user_id, export_id)
        if export.status == ExportStatus.REVOKED:
            raise ExportUnavailableError("Exportación revocada")
        if export.expires_at is not None and export.expires_at < utcnow():
            export.status = ExportStatus.EXPIRED
            export.content = None
            await self._exports.save(export)
            raise ExportExpiredError("Exportación expirada")
        if export.status != ExportStatus.READY or export.content is None:
            raise ExportUnavailableError("Exportación no disponible")
        return export, export.content.encode("utf-8")

    async def revoke(self, user_id: str, export_id: str) -> EmergencyExport:
        export = await self.get_export(user_id, export_id)
        export.status = ExportStatus.REVOKED
        export.content = None
        return await self._exports.save(export)

    async def _build_payload(
        self, user: User, sections: list[ExportSection]
    ) -> tuple[dict[str, Any], int]:
        selected = set(sections)
        data: dict[str, Any] = {}
        record_count = 0

        if ExportSection.PROFILE in selected:
            data["patient"] = {"full_name": user.full_name, "email": user.email}
            profile = await self._profiles.list_for_user(user.id, limit=1)
            if profile:
                data["profile"] = self._profile_dict(profile[0])
            record_count += 1

        if ExportSection.ALLERGIES in selected:
            allergies = [
                item
                for item in await self._allergies.list_for_user(
                    user.id, limit=1000
                )
                if item.is_emergency_relevant
            ]
            data["allergies"] = [self._allergy_dict(item) for item in allergies]
            record_count += len(allergies)

        if ExportSection.MEDICATIONS in selected:
            medications = [
                item
                for item in await self._medications.list_for_user(
                    user.id, limit=1000
                )
                if item.show_in_emergency and item.is_active
            ]
            data["medications"] = [
                self._medication_dict(item) for item in medications
            ]
            record_count += len(medications)

        if ExportSection.CONTACTS in selected:
            contacts = [
                item
                for item in await self._contacts.list_for_user(user.id, limit=1000)
                if item.is_active
            ]
            data["emergency_contacts"] = [
                self._contact_dict(item) for item in contacts
            ]
            record_count += len(contacts)

        if ExportSection.ALERTS in selected:
            alerts = [
                item
                for item in await self._alerts.list_for_user(user.id, limit=1000)
                if item.is_enabled
            ]
            data["alerts"] = [self._alert_dict(item) for item in alerts]
            record_count += len(alerts)

        return data, record_count

    @staticmethod
    def _profile_dict(profile: MedicalProfile) -> dict[str, Any]:
        return {
            "blood_type": profile.blood_type.value if profile.blood_type else None,
            "rh_factor": profile.rh_factor.value if profile.rh_factor else None,
            "date_of_birth": _iso(profile.date_of_birth),
            "height_cm": float(profile.height_cm)
            if profile.height_cm is not None
            else None,
            "weight_kg": float(profile.weight_kg)
            if profile.weight_kg is not None
            else None,
            "organ_donor": profile.organ_donor,
            "chronic_conditions": profile.chronic_conditions,
        }

    @staticmethod
    def _allergy_dict(allergy: Allergy) -> dict[str, Any]:
        return {
            "allergen_name": allergy.allergen_name,
            "category": allergy.category.value,
            "severity": allergy.severity.value,
            "status": allergy.status.value,
            "reaction": allergy.reaction,
            "diagnosed_at": _iso(allergy.diagnosed_at),
            "notes": allergy.notes,
        }

    @staticmethod
    def _medication_dict(medication: Medication) -> dict[str, Any]:
        return {
            "name": medication.name,
            "active_ingredient": medication.active_ingredient,
            "dosage": medication.dosage,
            "dose_unit": medication.dose_unit.value,
            "route": medication.route.value,
            "frequency_text": medication.frequency_text,
            "interval_hours": medication.interval_hours,
            "reminder_times": medication.reminder_times,
            "is_controlled": medication.is_controlled,
            "controlled_schedule": medication.controlled_schedule,
            "prescriber_name": medication.prescriber_name,
            "prescription_number": _mask(medication.prescription_number),
            "start_date": _iso(medication.start_date),
            "end_date": _iso(medication.end_date),
            "indication": medication.indication,
        }

    @staticmethod
    def _contact_dict(contact: EmergencyContact) -> dict[str, Any]:
        return {
            "full_name": contact.full_name,
            "relationship": contact.relationship,
            "phone_primary": contact.phone_primary,
            "phone_secondary": contact.phone_secondary,
            "email": contact.email,
            "priority": contact.priority,
        }

    @staticmethod
    def _alert_dict(alert: MedicalAlert) -> dict[str, Any]:
        return {
            "type": alert.type.value,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "scheduled_at": _iso(alert.scheduled_at),
            "recurrence_rule": alert.recurrence_rule,
            "timezone": alert.timezone,
        }


__all__ = [
    "ExportExpiredError",
    "ExportService",
    "ExportUnavailableError",
]
