"""Utilidades de tiempo en UTC.

SQLite no conserva el offset de zona horaria: `DateTime` devuelve valores
*naive*. Para que las comparaciones de expiración sean homogéneas se persiste
UTC sin tzinfo y se convierte a UTC consciente solo cuando se expone al cliente.
"""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Ahora en UTC sin tzinfo (formato que devuelve SQLite)."""
    return datetime.now(UTC).replace(tzinfo=None)


def naive_utc(value: datetime) -> datetime:
    """Normaliza cualquier instante a UTC sin tzinfo."""
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


def aware_utc(value: datetime) -> datetime:
    """Normaliza cualquier instante a UTC consciente."""
    if value.tzinfo is not None:
        return value.astimezone(UTC)
    return value.replace(tzinfo=UTC)


__all__ = ["utcnow", "naive_utc", "aware_utc"]
