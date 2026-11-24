"""Perfil clínico 1:1 con el usuario: tipo de sangre y datos base."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import BloodType, RhFactor
from app.models.health_mixin import HealthRecordMixin


class MedicalProfile(HealthRecordMixin, Base):
    __tablename__ = "medical_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_medical_profiles_user_id"),
    )

    blood_type: Mapped[BloodType | None] = mapped_column(
        Enum(
            BloodType,
            native_enum=False,
            create_constraint=True,
            name="blood_type",
        ),
        nullable=True,
    )
    rh_factor: Mapped[RhFactor | None] = mapped_column(
        Enum(
            RhFactor,
            native_enum=False,
            create_constraint=True,
            name="rh_factor",
        ),
        nullable=True,
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    organ_donor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    chronic_conditions: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    def __repr__(self) -> str:
        return f"<MedicalProfile user_id={self.user_id!r} blood_type={self.blood_type}>"
