"""Esquemas Pydantic de las entidades clínicas.

Toda entrada usa `extra="forbid"`, longitudes acotadas, enums cerrados y
rechazo de markup/caracteres de control. El `user_id` nunca se acepta del
cliente: se deriva del JWT. Los campos sensibles del export (hash del token de
descarga y ubicación del blob) no se exponen en las respuestas.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.models.enums import (
    AlertDelivery,
    AlertRelatedType,
    AlertSeverity,
    AlertType,
    AllergyCategory,
    AllergySeverity,
    AllergyStatus,
    BloodType,
    DoseUnit,
    ExportFormat,
    ExportSection,
    ExportStatus,
    MedicationRoute,
    RhFactor,
)


def _reject_markup(value: str) -> str:
    if "<" in value or ">" in value:
        raise ValueError("No se permite HTML/markup en este campo")
    if any(ord(char) < 32 and char not in "\n\t" for char in value):
        raise ValueError("No se permiten caracteres de control")
    return value


NameText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    AfterValidator(_reject_markup),
]
ShortText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=60),
    AfterValidator(_reject_markup),
]
ScheduleText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=20),
    AfterValidator(_reject_markup),
]
MediumText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    AfterValidator(_reject_markup),
]
LongText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
    AfterValidator(_reject_markup),
]
NotesText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
    AfterValidator(_reject_markup),
]
PhoneText = Annotated[
    str,
    StringConstraints(pattern=r"^\+[1-9]\d{1,14}$"),
]
UuidText = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
    ),
]
TimeOfDay = Annotated[
    str,
    StringConstraints(pattern=r"^([01]\d|2[0-3]):[0-5]\d$"),
]


class HealthSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


# --------------------------------------------------------------------------- #
# Perfil clínico
# --------------------------------------------------------------------------- #


class MedicalProfileCreate(HealthSchema):
    id: UuidText | None = None
    blood_type: BloodType | None = None
    rh_factor: RhFactor | None = None
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=1000)
    organ_donor: bool | None = None
    chronic_conditions: NotesText | None = None


class MedicalProfileUpdate(HealthSchema):
    blood_type: BloodType | None = None
    rh_factor: RhFactor | None = None
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=1000)
    organ_donor: bool | None = None
    chronic_conditions: NotesText | None = None


class MedicalProfileOut(HealthSchema):
    id: str
    user_id: str
    blood_type: BloodType | None
    rh_factor: RhFactor | None
    date_of_birth: date | None
    height_cm: float | None
    weight_kg: float | None
    organ_donor: bool | None
    chronic_conditions: str | None
    version: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- #
# Alergias
# --------------------------------------------------------------------------- #


class AllergyCreate(HealthSchema):
    id: UuidText | None = None
    allergen_name: NameText
    category: AllergyCategory
    severity: AllergySeverity
    status: AllergyStatus = AllergyStatus.ACTIVE
    reaction: MediumText | None = None
    diagnosed_at: date | None = None
    notes: LongText | None = None
    is_emergency_relevant: bool = True


class AllergyUpdate(HealthSchema):
    allergen_name: NameText | None = None
    category: AllergyCategory | None = None
    severity: AllergySeverity | None = None
    status: AllergyStatus | None = None
    reaction: MediumText | None = None
    diagnosed_at: date | None = None
    notes: LongText | None = None
    is_emergency_relevant: bool | None = None


class AllergyOut(HealthSchema):
    id: str
    user_id: str
    allergen_name: str
    category: AllergyCategory
    severity: AllergySeverity
    status: AllergyStatus
    reaction: str | None
    diagnosed_at: date | None
    notes: str | None
    is_emergency_relevant: bool
    version: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- #
# Medicamentos
# --------------------------------------------------------------------------- #


class MedicationCreate(HealthSchema):
    id: UuidText | None = None
    name: NameText
    active_ingredient: NameText | None = None
    dosage: ShortText
    dose_unit: DoseUnit
    route: MedicationRoute
    frequency_text: NameText
    interval_hours: int | None = Field(default=None, ge=1, le=168)
    reminder_times: list[TimeOfDay] = Field(default_factory=list, max_length=12)
    is_controlled: bool = False
    controlled_schedule: ScheduleText | None = None
    prescriber_name: NameText | None = None
    prescription_number: ShortText | None = None
    start_date: date
    end_date: date | None = None
    is_active: bool = True
    indication: MediumText | None = None
    show_in_emergency: bool = True

    @field_validator("reminder_times")
    @classmethod
    def _unique_reminder_times(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("Los horarios de recordatorio no deben repetirse")
        return value

    @model_validator(mode="after")
    def _validate_rules(self) -> MedicationCreate:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date no puede ser anterior a start_date")
        if self.controlled_schedule is not None and not self.is_controlled:
            raise ValueError("controlled_schedule exige is_controlled = true")
        if self.is_controlled and self.prescriber_name is None:
            raise ValueError("Un medicamento controlado exige prescriber_name")
        return self


class MedicationUpdate(HealthSchema):
    name: NameText | None = None
    active_ingredient: NameText | None = None
    dosage: ShortText | None = None
    dose_unit: DoseUnit | None = None
    route: MedicationRoute | None = None
    frequency_text: NameText | None = None
    interval_hours: int | None = Field(default=None, ge=1, le=168)
    reminder_times: list[TimeOfDay] | None = Field(default=None, max_length=12)
    is_controlled: bool | None = None
    controlled_schedule: ScheduleText | None = None
    prescriber_name: NameText | None = None
    prescription_number: ShortText | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    indication: MediumText | None = None
    show_in_emergency: bool | None = None

    @field_validator("reminder_times")
    @classmethod
    def _unique_reminder_times(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and len(set(value)) != len(value):
            raise ValueError("Los horarios de recordatorio no deben repetirse")
        return value

    @model_validator(mode="after")
    def _validate_rules(self) -> MedicationUpdate:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date no puede ser anterior a start_date")
        if self.controlled_schedule is not None and self.is_controlled is False:
            raise ValueError("controlled_schedule exige is_controlled = true")
        return self


class MedicationOut(HealthSchema):
    id: str
    user_id: str
    name: str
    active_ingredient: str | None
    dosage: str
    dose_unit: DoseUnit
    route: MedicationRoute
    frequency_text: str
    interval_hours: int | None
    reminder_times: list[str]
    is_controlled: bool
    controlled_schedule: str | None
    prescriber_name: str | None
    prescription_number: str | None
    start_date: date
    end_date: date | None
    is_active: bool
    indication: str | None
    show_in_emergency: bool
    version: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- #
# Contactos de emergencia
# --------------------------------------------------------------------------- #


class EmergencyContactCreate(HealthSchema):
    id: UuidText | None = None
    full_name: NameText
    relationship: ShortText
    phone_primary: PhoneText
    phone_secondary: PhoneText | None = None
    email: EmailStr | None = None
    priority: int = Field(ge=0, le=99)
    notify_on_incident: bool = True
    is_active: bool = True
    notes: MediumText | None = None


class EmergencyContactUpdate(HealthSchema):
    full_name: NameText | None = None
    relationship: ShortText | None = None
    phone_primary: PhoneText | None = None
    phone_secondary: PhoneText | None = None
    email: EmailStr | None = None
    priority: int | None = Field(default=None, ge=0, le=99)
    notify_on_incident: bool | None = None
    is_active: bool | None = None
    notes: MediumText | None = None


class EmergencyContactOut(HealthSchema):
    id: str
    user_id: str
    full_name: str
    relationship: str
    phone_primary: str
    phone_secondary: str | None
    email: EmailStr | None
    priority: int
    notify_on_incident: bool
    is_active: bool
    notes: str | None
    version: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- #
# Exportación del historial clínico
# --------------------------------------------------------------------------- #


class EmergencyExportCreate(HealthSchema):
    format: ExportFormat
    sections: list[ExportSection] = Field(
        default_factory=lambda: list(ExportSection),
        min_length=1,
        max_length=len(ExportSection),
    )

    @field_validator("sections")
    @classmethod
    def _unique_sections(cls, value: list[ExportSection]) -> list[ExportSection]:
        if len(set(value)) != len(value):
            raise ValueError("Las secciones del export no deben repetirse")
        return value


class EmergencyExportOut(HealthSchema):
    id: str
    user_id: str
    format: ExportFormat
    status: ExportStatus
    sections: list[ExportSection]
    strategy: str
    strategy_version: str
    requested_at: datetime
    generated_at: datetime | None
    expires_at: datetime | None
    content_sha256: str | None
    size_bytes: int | None
    record_count: int | None
    error_code: str | None


# --------------------------------------------------------------------------- #
# Alertas médicas
# --------------------------------------------------------------------------- #


class MedicalAlertCreate(HealthSchema):
    id: UuidText | None = None
    type: AlertType
    severity: AlertSeverity
    title: NameText
    message: LongText
    related_type: AlertRelatedType = AlertRelatedType.NONE
    related_id: UuidText | None = None
    scheduled_at: datetime | None = None
    recurrence_rule: MediumText | None = None
    timezone: str = Field(default="UTC", min_length=1, max_length=64)
    is_enabled: bool = True
    escalate_to_contact_id: UuidText | None = None
    delivery: AlertDelivery = AlertDelivery.LOCAL_NOTIFICATION

    @model_validator(mode="after")
    def _validate_rules(self) -> MedicalAlertCreate:
        if self.scheduled_at is not None and self.recurrence_rule is not None:
            raise ValueError("scheduled_at y recurrence_rule son mutuamente excluyentes")
        if self.type == AlertType.MEDICATION_REMINDER and (
            self.scheduled_at is None and self.recurrence_rule is None
        ):
            raise ValueError("Un recordatorio de medicamento exige programación")
        if self.related_type == AlertRelatedType.NONE and self.related_id is not None:
            raise ValueError("related_id no aplica cuando related_type = NONE")
        if self.related_type != AlertRelatedType.NONE and self.related_id is None:
            raise ValueError("related_type distinto de NONE exige related_id")
        return self


class MedicalAlertUpdate(HealthSchema):
    type: AlertType | None = None
    severity: AlertSeverity | None = None
    title: NameText | None = None
    message: LongText | None = None
    related_type: AlertRelatedType | None = None
    related_id: UuidText | None = None
    scheduled_at: datetime | None = None
    recurrence_rule: MediumText | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    is_enabled: bool | None = None
    escalate_to_contact_id: UuidText | None = None
    delivery: AlertDelivery | None = None

    @model_validator(mode="after")
    def _validate_rules(self) -> MedicalAlertUpdate:
        if self.scheduled_at is not None and self.recurrence_rule is not None:
            raise ValueError("scheduled_at y recurrence_rule son mutuamente excluyentes")
        if self.related_type == AlertRelatedType.NONE and self.related_id is not None:
            raise ValueError("related_id no aplica cuando related_type = NONE")
        if (
            self.related_type is not None
            and self.related_type != AlertRelatedType.NONE
            and self.related_id is None
        ):
            raise ValueError("related_type distinto de NONE exige related_id")
        return self


class MedicalAlertOut(HealthSchema):
    id: str
    user_id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    related_type: AlertRelatedType
    related_id: str | None
    scheduled_at: datetime | None
    recurrence_rule: str | None
    timezone: str
    is_enabled: bool
    next_fire_at: datetime | None
    last_fired_at: datetime | None
    acknowledged_at: datetime | None
    snoozed_until: datetime | None
    escalate_to_contact_id: str | None
    delivery: AlertDelivery
    version: int
    created_at: datetime
    updated_at: datetime
