# app/routes/__init__.py
# ÚNICO punto de entrada de rutas del proyecto
from fastapi import APIRouter

from app.routes.api_v1 import router as api_v1

router = APIRouter()
router.include_router(api_v1)
