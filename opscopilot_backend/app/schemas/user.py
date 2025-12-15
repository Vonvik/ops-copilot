# app/schemas/user.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Esquemas de entrada ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None
    role: str | None = "user"  # "user" | "admin"


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


# ---------- Esquemas de salida (respuesta API) ----------
class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    # Pydantic v2: permite construir desde objetos ORM (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)
