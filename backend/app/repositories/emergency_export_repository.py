"""Repositorio de snapshots de exportación (acotado por usuario)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emergency_export import EmergencyExport


class EmergencyExportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(
        self, user_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[EmergencyExport]:
        stmt = (
            select(EmergencyExport)
            .where(EmergencyExport.user_id == user_id)
            .order_by(EmergencyExport.requested_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_for_user(
        self, user_id: str, export_id: str
    ) -> EmergencyExport | None:
        stmt = select(EmergencyExport).where(
            EmergencyExport.id == export_id,
            EmergencyExport.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, export: EmergencyExport) -> EmergencyExport:
        self._session.add(export)
        await self._session.commit()
        await self._session.refresh(export)
        return export
