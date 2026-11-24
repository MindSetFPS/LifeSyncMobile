"""Alergia del paciente. `is_emergency_relevant` la incluye en el export."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import (
    AllergyCategory,
    AllergySeverity,
    AllergyStatus,
)
from app.models.health_mixin import HealthRecordMixin


class Allergy(HealthRecordMixin, Base):
    __tablename__ = "allergies"

    allergen_name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[AllergyCategory] = mapped_column(
        Enum(
            AllergyCategory,
            native_enum=False,
            create_constraint=True,
            name="allergy_category",
        ),
        nullable=False,
    )
    severity: Mapped[AllergySeverity] = mapped_column(
        Enum(
            AllergySeverity,
            native_enum=False,
            create_constraint=True,
            name="allergy_severity",
        ),
        nullable=False,
    )
    status: Mapped[AllergyStatus] = mapped_column(
        Enum(
            AllergyStatus,
            native_enum=False,
            create_constraint=True,
            name="allergy_status",
        ),
        default=AllergyStatus.ACTIVE,
        nullable=False,
    )
    reaction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    diagnosed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_emergency_relevant: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Allergy id={self.id!r} name={self.allergen_name!r}>"
