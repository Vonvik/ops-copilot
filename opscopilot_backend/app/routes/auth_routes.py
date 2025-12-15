# app/routes/auth_routes.py
from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.get("/auth/health")
def auth_health():
    """
    Endpoint mínimo para que el router 'auth_routes' exista y el include del main no falle.
    Sustituye o amplía con tus endpoints reales de login/refresh/logout cuando los tengas.
    """
    return {"status": "ok", "area": "auth"}
