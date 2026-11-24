"""Alerta médica local (recordatorios y avisos de emergencia).

El módulo de alertas vive en el dispositivo (Observer + notificación local);
esta tabla permite además respaldarla de forma cifrada en la nube.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import (
    AlertDelivery,
    AlertRelatedType,
    AlertSeverity,
    AlertType,
)
from app.models.health_mixin import HealthRecordMixin


class MedicalAlert(HealthRecordMixin, Base):
    __tablename__ = "medical_alerts"
    __table_args__ = (
        CheckConstraint(
            "scheduled_at IS NULL OR recurrence_rule IS NULL",
            name="ck_medical_alerts_schedule_exclusive",
        ),
        CheckConstraint(
            "related_type = 'NONE' OR related_id IS NOT NULL",
            name="ck_medical_alerts_related_id",
        ),
    )

    type: Mapped[AlertType] = mapped_column(
        Enum(
            AlertType,
            native_enum=False,
            create_constraint=True,
            name="alert_type",
        ),
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(
            AlertSeverity,
            native_enum=False,
            create_constraint=True,
            name="alert_severity",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    related_type: Mapped[AlertRelatedType] = mapped_column(
        Enum(
            AlertRelatedType,
            native_enum=False,
            create_constraint=True,
            name="alert_related_type",
        ),
        default=AlertRelatedType.NONE,
        nullable=False,
    )
    related_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(64), default="UTC", nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    next_fire_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_fired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    snoozed_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    escalate_to_contact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("emergency_contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    delivery: Mapped[AlertDelivery] = mapped_column(
        Enum(
            AlertDelivery,
            native_enum=False,
            create_constraint=True,
            name="alert_delivery",
        ),
        default=AlertDelivery.LOCAL_NOTIFICATION,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<MedicalAlert id={self.id!r} type={self.type} enabled={self.is_enabled}>"
