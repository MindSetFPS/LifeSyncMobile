"""Punto de entrada de la API centralizada de LifeSync Mobile."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import database
from app.core.security import ensure_rsa_keypair


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Arranque: genera llaves RSA, inicializa el Singleton de DB y el esquema."""
    ensure_rsa_keypair()
    database.init()
    await database.create_all()
    yield
    await database.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="API de autenticación OAuth2/JWT para LifeSync Mobile (Sprint 1)",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"], summary="Health check")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENVIRONMENT}
