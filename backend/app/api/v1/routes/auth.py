"""Rutas de autenticación: registro, token OAuth 2.0, refresh y perfil."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CurrentUser
from app.core.database import get_db
from app.schemas.auth import RefreshRequest, Token, UserCreate, UserOut
from app.services.auth_service import (
    AuthService,
    EmailAlreadyExists,
    InvalidCredentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
async def register(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    service = AuthService(session)
    try:
        return await service.register(payload)
    except EmailAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post("/token", response_model=Token, summary="OAuth 2.0 password grant")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Valida credenciales y devuelve un JWT firmado criptográficamente."""
    service = AuthService(session)
    try:
        user = await service.authenticate(form.username, form.password)
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return service.issue_tokens(user)


@router.post("/refresh", response_model=Token, summary="Renovar access token")
async def refresh(
    payload: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    service = AuthService(session)
    try:
        return await service.refresh(payload.refresh_token)
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc


@router.get("/me", response_model=UserOut, summary="Perfil del usuario autenticado")
async def read_me(current_user: CurrentUser) -> User:
    return current_user
