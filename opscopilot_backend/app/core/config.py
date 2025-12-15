# app/core/config.py
from __future__ import annotations

import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_origins(items: list[str]) -> list[str]:
    return [str(x).strip().rstrip("/") for x in items if str(x).strip()]


def _parse_raw_origins(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("[") and raw.endswith("]"):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return _normalize_origins([str(x) for x in data])
        except json.JSONDecodeError:
            # invalid JSON, fall back to comma-splitting below
            pass
    return _normalize_origins(raw.split(","))


class Settings(BaseSettings):
    """
    Settings unificados (Pydantic v2), coherentes con todo el proyecto.
    - CORS: CORS_ORIGINS, CORS_ALLOW_ORIGINS, CORS_ORIGINS_RAW.
    - Celery/Redis: REDIS_URL o explícitos CELERY_BROKER_URL/RESULT_BACKEND.
    - Auth, rate-limits, frontend y extras ya usados en el código.
    """

    # --- Entorno ---
    ENV: str = Field(default="development")

    # --- DB ---
    DATABASE_URL: str

    # --- Auth/JWT ---
    SECRET_KEY: str = Field(default="CHANGE_ME")
    ALGORITHM: str = Field(default="HS256")
    JWT_ALGORITHM: str = Field(default="HS256")  # compat si tu código lo lee
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=43200)  # 30 días
    RESET_TOKEN_SECRET: str = Field(default="CHANGE_ME_RESET")
    RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    SECURE_COOKIES: bool = Field(default=False)

    # --- Rate limits / Frontend ---
    RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=5)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=300)
    RATE_LIMIT_BLOCK_SECONDS: int = Field(default=900)
    FRONTEND_URL: str = Field(default="http://localhost:5173")

    # --- Notificaciones (opcional en este sprint) ---
    NOTIFY_EMAIL: str | None = None

    # --- Redis / Celery ---
    REDIS_URL: str | None = None
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # --- CORS (3 formas soportadas) ---
    CORS_ORIGINS: list[str] = Field(default_factory=list)
    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=list)
    CORS_ORIGINS_RAW: str = Field(default="")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ----------------- Helpers -----------------
    def cors_origins(self) -> list[str]:
        if self.CORS_ORIGINS:
            return _normalize_origins(self.CORS_ORIGINS)
        if self.CORS_ALLOW_ORIGINS:
            return _normalize_origins(self.CORS_ALLOW_ORIGINS)
        if self.CORS_ORIGINS_RAW:
            return _parse_raw_origins(self.CORS_ORIGINS_RAW)
        return []

    def celery_urls(self) -> tuple[str, str]:
        """
        Prioridad:
          1) CELERY_BROKER_URL / CELERY_RESULT_BACKEND
          2) REDIS_URL -> deriva /0 (broker) y /1 (backend) respetando db si viene dada
          3) Defaults dev
        """
        if self.CELERY_BROKER_URL and self.CELERY_RESULT_BACKEND:
            return self.CELERY_BROKER_URL, self.CELERY_RESULT_BACKEND

        if self.REDIS_URL:
            base = self.REDIS_URL.rstrip("/")
            last = base.rsplit("/", 1)[-1]
            if last.isdigit():
                broker = base
                prefix = base.rsplit("/", 1)[0]
                backend = f"{prefix}/1"
            else:
                broker = f"{base}/0"
                backend = f"{base}/1"
            return broker, backend

        return "redis://localhost:6379/0", "redis://localhost:6379/1"


settings = Settings()
