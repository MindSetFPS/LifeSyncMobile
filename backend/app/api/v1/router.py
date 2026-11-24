"""Ensamblador de routers de la API v1."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import auth, oauth_authorize

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(oauth_authorize.router)

__all__ = ["api_router"]
