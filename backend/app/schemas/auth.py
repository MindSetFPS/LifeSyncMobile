"""Esquemas Pydantic de autenticación y respuesta de usuario."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Cuerpo de registro. La contraseña nunca se devuelve."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Respuesta OAuth 2.0: bearer + refresh token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str = "read write"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)
