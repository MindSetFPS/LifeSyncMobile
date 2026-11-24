"""Servicio genérico de CRUD clínico con control de propiedad (anti-IDOR)."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base
from app.repositories.health_repository import HealthRepository

ModelT = TypeVar("ModelT", bound=Base)


class NotFoundError(Exception):
    """El registro no existe o pertenece a otro usuario (mismo 404)."""


class ConflictError(Exception):
    """Conflicto de unicidad o regla de negocio."""


class HealthService(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._repo = HealthRepository(session, model)

    async def list_records(
        self, user_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[ModelT]:
        return await self._repo.list_for_user(user_id, limit=limit, offset=offset)

    async def get_record(self, user_id: str, record_id: str) -> ModelT:
        record = await self._repo.get_for_user(user_id, record_id)
        if record is None:
            raise NotFoundError("Registro no encontrado")
        return record

    async def get_single(self, user_id: str) -> ModelT | None:
        records = await self._repo.list_for_user(user_id, limit=1)
        return records[0] if records else None

    async def create_record(self, user_id: str, payload: BaseModel) -> ModelT:
        data: dict[str, Any] = payload.model_dump()
        record_id = data.get("id")
        if record_id is not None:
            existing = await self._repo.get_by_id(record_id)
            if existing is not None:
                if existing.user_id == user_id and existing.deleted_at is None:
                    return existing
                raise ConflictError("No se pudo crear el registro")
        try:
            return await self._repo.create(user_id, data)
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("Conflicto con un registro existente") from exc

    async def update_record(
        self, user_id: str, record_id: str, payload: BaseModel
    ) -> ModelT:
        record = await self.get_record(user_id, record_id)
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return record
        try:
            return await self._repo.update(record, data)
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("Conflicto con un registro existente") from exc

    async def delete_record(self, user_id: str, record_id: str) -> None:
        record = await self.get_record(user_id, record_id)
        await self._repo.soft_delete(record)


__all__ = ["ConflictError", "HealthService", "NotFoundError"]
