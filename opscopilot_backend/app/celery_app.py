# app/celery_app.py
from __future__ import annotations

import os

from celery import Celery

from app.core.config import settings

# Normaliza URLs desde settings (compatibles con Celery)
broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
result_backend = settings.CELERY_RESULT_BACKEND or settings.REDIS_URL

os.environ.setdefault("CELERY_BROKER_URL", broker_url or "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", result_backend or "redis://localhost:6379/0")

celery = Celery(
    "ops_copilot",
    broker=os.environ["CELERY_BROKER_URL"],
    backend=os.environ["CELERY_RESULT_BACKEND"],
    include=["app.tasks.csv_tasks"],  # ← asegura que cargue este módulo
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
