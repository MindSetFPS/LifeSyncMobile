"""DeclarativeBase compartido por todos los modelos."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base del esquema ORM."""
