"""Repositorio genérico de registros clínicos.

Todas las consultas están acotadas por `user_id`: es la defensa contra IDOR.
El `user_id` proviene del JWT, nunca del cuerpo de la petición.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutils import utcnow
from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class HealthRepository(Generic[ModelT]):
    """Acceso a una tabla clínica con propiedad obligatoria por usuario."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def list_for_user(
        self,
        user_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelT]:
        stmt = (
            select(self._model)
            .where(
                self._model.user_id == user_id,
                self._model.deleted_at.is_(None),
            )
            .order_by(self._model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_user(self, user_id: str, record_id: str) -> ModelT | None:
        stmt = select(self._model).where(
            self._model.id == record_id,
            self._model.user_id == user_id,
            self._model.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, record_id: str) -> ModelT | None:
        return await self._session.get(self._model, record_id)

    async def create(self, user_id: str, data: dict[str, Any]) -> ModelT:
        record_id = data.pop("id", None)
        record = self._model(user_id=user_id, **data)
        if record_id is not None:
            record.id = record_id
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def update(self, record: ModelT, data: dict[str, Any]) -> ModelT:
        for field, value in data.items():
            setattr(record, field, value)
        record.version += 1
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def soft_delete(self, record: ModelT) -> None:
        record.deleted_at = utcnow()
        record.version += 1
        await self._session.commit()
