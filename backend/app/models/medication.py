"""Medicamento del paciente, incluidos los controlados."""

from __future__ import annotations

from datetime import date

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import DoseUnit, MedicationRoute
from app.models.health_mixin import HealthRecordMixin


class Medication(HealthRecordMixin, Base):
    __tablename__ = "medications"
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_medications_dates",
        ),
        CheckConstraint(
            "interval_hours IS NULL OR (interval_hours >= 1 AND interval_hours <= 168)",
            name="ck_medications_interval_hours",
        ),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    active_ingredient: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dosage: Mapped[str] = mapped_column(String(60), nullable=False)
    dose_unit: Mapped[DoseUnit] = mapped_column(
        Enum(
            DoseUnit,
            native_enum=False,
            create_constraint=True,
            name="dose_unit",
        ),
        nullable=False,
    )
    route: Mapped[MedicationRoute] = mapped_column(
        Enum(
            MedicationRoute,
            native_enum=False,
            create_constraint=True,
            name="medication_route",
        ),
        nullable=False,
    )
    frequency_text: Mapped[str] = mapped_column(String(120), nullable=False)
    interval_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reminder_times: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    controlled_schedule: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prescriber_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prescription_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    indication: Mapped[str | None] = mapped_column(String(255), nullable=True)
    show_in_emergency: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Medication id={self.id!r} name={self.name!r} controlled={self.is_controlled}>"
