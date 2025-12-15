from fastapi import APIRouter

router = APIRouter(prefix="", tags=["health"])


@router.get("/")
def root():
    return {"status": "ok", "service": "Ops-Copilot Backend"}


@router.get("/ping")
def ping():
    return {"ping": "pong"}
