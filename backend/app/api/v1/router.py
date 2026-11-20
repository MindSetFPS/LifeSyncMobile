"""Ensamblador de routers de la API v1."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import auth

api_router = APIRouter()
api_router.include_router(auth.router)

__all__ = ["api_router"]
