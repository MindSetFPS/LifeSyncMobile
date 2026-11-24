"""Contacto de emergencia con prioridad única por usuario (0 = principal)."""

from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.health_mixin import HealthRecordMixin


class EmergencyContact(HealthRecordMixin, Base):
    __tablename__ = "emergency_contacts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "priority",
            name="uq_emergency_contacts_user_priority",
        ),
        CheckConstraint("priority >= 0", name="ck_emergency_contacts_priority"),
    )

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    relationship: Mapped[str] = mapped_column(String(60), nullable=False)
    phone_primary: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_secondary: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    notify_on_incident: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<EmergencyContact id={self.id!r} priority={self.priority}>"
