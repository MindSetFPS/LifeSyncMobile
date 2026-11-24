"""Punto de entrada de la API centralizada de LifeSync Mobile."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.api.well_known import router as well_known_router
from app.core.auth_middleware import BearerAuthMiddleware
from app.core.config import settings
from app.core.database import database
from app.core.oauth import OAuthError, oauth_error_handler
from app.core.security import ensure_rsa_keypair
from app.services.client_service import ClientService


async def _seed_oauth_client() -> None:
    """Registra el cliente público de la app móvil si aún no existe."""
    async with database.session_factory() as session:
        service = ClientService(session)
        if await service.get(settings.OAUTH_SEED_CLIENT_ID) is not None:
            return
        redirect_uris = [
            uri.strip()
            for uri in settings.OAUTH_SEED_CLIENT_REDIRECT_URIS.split(",")
            if uri.strip()
        ]
        await service.register_client(
            client_id=settings.OAUTH_SEED_CLIENT_ID,
            client_name="LifeSync Mobile (Android)",
            redirect_uris=redirect_uris,
            allowed_scopes=settings.OAUTH_SUPPORTED_SCOPES,
            is_public=True,
        )
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Arranque: genera llaves RSA, inicializa el Singleton de DB y el esquema."""
    ensure_rsa_keypair()
    database.init()
    await database.create_all()
    await _seed_oauth_client()
    yield
    await database.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.2.0",
    description="API OAuth 2.0 / JWT para LifeSync Mobile (Sprint 1 extendido)",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
)

app.add_middleware(BearerAuthMiddleware)
app.add_exception_handler(OAuthError, oauth_error_handler)
app.include_router(well_known_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"], summary="Health check")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENVIRONMENT}
