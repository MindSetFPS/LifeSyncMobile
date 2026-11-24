"""Capa de persistencia con conexión centralizada (patrón Singleton).

Se garantiza una única instancia del engine y del sessionmaker para todo el
proceso. El engine se crea de forma diferida (lazy) para que las pruebas puedan
sustituir la URL de la base de datos antes de la primera conexión.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class DatabaseManager:
    """Singleton que administra el engine y el pool de sesiones asíncronas."""

    _instance: DatabaseManager | None = None
    _initialized: bool = False

    def __new__(cls) -> DatabaseManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init(self, database_url: str | None = None, echo: bool = False) -> None:
        """Inicializa el engine una sola vez. Llamadas posteriores son ignoradas."""
        if self._initialized:
            return
        url = database_url or settings.DATABASE_URL
        self.engine: AsyncEngine = create_async_engine(
            url,
            echo=echo,
            pool_pre_ping=True,
            future=True,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        self._initialized = True

    def reset(self) -> None:
        """Solo para pruebas: descarta el estado del singleton."""
        self._initialized = False
        self._instance = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependencia de FastAPI: entrega una sesión y siempre la cierra."""
        if not self._initialized:
            self.init()
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_all(self) -> None:
        """Crea el esquema. Requiere que los modelos estén importados."""
        if not self._initialized:
            self.init()
        from app import models  # noqa: F401  (registro de todos los metadatos)

        async with self.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

    async def dispose(self) -> None:
        if self._initialized:
            await self.engine.dispose()


database = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Punto de entrada único para la inyección de dependencias de sesión."""
    async for session in database.get_session():
        yield session


def get_database_manager() -> DatabaseManager:
    """Permite inyectar el administrador (y hacer mock en pruebas)."""
    return database


__all__ = ["DatabaseManager", "database", "get_db", "get_database_manager"]
