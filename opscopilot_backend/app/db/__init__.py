# app/db/__init__.py
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Usa la DATABASE_URL centralizada (pydantic-settings ya leyó .env)
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada en .env")

# Engine SQLAlchemy 2.x
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,  # habilita API 2.x
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,  # API 2.x
)

# Base declarativa
Base = declarative_base()


# Dependencia FastAPI
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "Base", "get_db", "DATABASE_URL"]
