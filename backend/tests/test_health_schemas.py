"""Pruebas de validación y sanitización de los esquemas clínicos."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.models.enums import (
    AlertRelatedType,
    AlertSeverity,
    AlertType,
    AllergyCategory,
    AllergySeverity,
    BloodType,
    DoseUnit,
    ExportFormat,
    ExportSection,
    MedicationRoute,
)
from app.schemas.health import (
    AllergyCreate,
    EmergencyContactCreate,
    EmergencyExportCreate,
    EmergencyExportOut,
    MedicalAlertCreate,
    MedicalProfileCreate,
    MedicationCreate,
)


def test_health_tables_registered() -> None:
    from app import models

    expected = {
        "medical_profiles",
        "allergies",
        "medications",
        "emergency_contacts",
        "emergency_exports",
        "medical_alerts",
    }
    assert expected.issubset(models.Base.metadata.tables)


def test_profile_normalizes_text_and_enum() -> None:
    profile = MedicalProfileCreate(
        blood_type="O",
        rh_factor="POSITIVE",
        chronic_conditions="  Hipertensión  ",
    )
    assert profile.blood_type is BloodType.O
    assert profile.chronic_conditions == "Hipertensión"


@pytest.mark.parametrize("blood_type", ["C", "o+", "", 42])
def test_profile_rejects_invalid_blood_type(blood_type: object) -> None:
    with pytest.raises(ValidationError):
        MedicalProfileCreate(blood_type=blood_type)


def test_allergy_rejects_markup_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AllergyCreate(
            allergen_name="<script>alert(1)</script>",
            category=AllergyCategory.MEDICATION,
            severity=AllergySeverity.SEVERE,
        )

    with pytest.raises(ValidationError):
        AllergyCreate(
            allergen_name="Penicilina",
            category=AllergyCategory.MEDICATION,
            severity=AllergySeverity.SEVERE,
            user_id="00000000-0000-0000-0000-000000000000",
        )


def test_medication_controlled_rules() -> None:
    base = {
        "name": "Tramadol",
        "dosage": "50",
        "dose_unit": DoseUnit.MG,
        "route": MedicationRoute.ORAL,
        "frequency_text": "Cada 8 horas",
        "start_date": date(2026, 1, 1),
    }

    with pytest.raises(ValidationError):
        MedicationCreate(**base, is_controlled=True)

    with pytest.raises(ValidationError):
        MedicationCreate(**base, controlled_schedule="II")

    medication = MedicationCreate(
        **base,
        is_controlled=True,
        controlled_schedule="II",
        prescriber_name="Dra. Pérez",
        reminder_times=["08:00", "20:00"],
    )
    assert medication.is_controlled is True
    assert medication.reminder_times == ["08:00", "20:00"]


def test_medication_rejects_end_before_start_and_duplicate_times() -> None:
    base = {
        "name": "Ibuprofeno",
        "dosage": "400",
        "dose_unit": DoseUnit.MG,
        "route": MedicationRoute.ORAL,
        "frequency_text": "Cada 12 horas",
        "start_date": date(2026, 2, 1),
    }
    with pytest.raises(ValidationError):
        MedicationCreate(**base, end_date=date(2026, 1, 1))
    with pytest.raises(ValidationError):
        MedicationCreate(**base, reminder_times=["08:00", "08:00"])


def test_emergency_contact_requires_e164_and_priority() -> None:
    with pytest.raises(ValidationError):
        EmergencyContactCreate(
            full_name="Ana",
            relationship="Madre",
            phone_primary="555-1234",
            priority=0,
        )

    contact = EmergencyContactCreate(
        full_name="  Ana  ",
        relationship=" Madre ",
        phone_primary="+5215555555555",
        priority=0,
    )
    assert contact.full_name == "Ana"
    assert contact.phone_primary == "+5215555555555"


def test_export_sections_are_unique_and_not_exposed_hashes() -> None:
    export = EmergencyExportCreate(
        format=ExportFormat.JSON,
        sections=[ExportSection.PROFILE, ExportSection.ALLERGIES],
    )
    assert export.format is ExportFormat.JSON

    with pytest.raises(ValidationError):
        EmergencyExportCreate(
            format=ExportFormat.CSV,
            sections=[ExportSection.PROFILE, ExportSection.PROFILE],
        )

    assert "storage_key" not in EmergencyExportOut.model_fields
    assert "download_token_hash" not in EmergencyExportOut.model_fields


def test_alert_schedule_rules() -> None:
    base = {
        "type": AlertType.MEDICATION_REMINDER,
        "severity": AlertSeverity.HIGH,
        "title": "Tomar medicamento",
        "message": "Tramadol 50 mg",
    }

    with pytest.raises(ValidationError):
        MedicalAlertCreate(**base)

    with pytest.raises(ValidationError):
        MedicalAlertCreate(
            **base,
            scheduled_at="2026-01-01T08:00:00",
            recurrence_rule="FREQ=DAILY",
        )

    alert = MedicalAlertCreate(
        **base,
        recurrence_rule="FREQ=DAILY",
        related_type=AlertRelatedType.MEDICATION,
        related_id="11111111-1111-1111-1111-111111111111",
    )
    assert alert.recurrence_rule == "FREQ=DAILY"
