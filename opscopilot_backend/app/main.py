# app/main.py
from __future__ import annotations

import importlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.ratelimit import limiter
from app.api.routes.users import router
from app.api.routes import auth as auth_routes

# -------------------- Settings seguros --------------------
try:
    from app.core.config import settings  # type: ignore[attr-defined]
except ImportError:

    class _S:  # noqa: N801
        ENV = "development"
        CORS_ORIGINS: list[str] = []
        CORS_ALLOW_ORIGINS: list[str] = []
        CORS_ALLOW_CREDENTIALS: bool = True

    settings = _S()  # type: ignore[assignment]


# -------------------- Lifespan preferente --------------------
def _import_optional(dotted: str, attr: str) -> object | None:
    try:
        mod = importlib.import_module(dotted)
        return getattr(mod, attr, None)
    except (ImportError, ModuleNotFoundError):
        return None


def _get_lifespan():
    # 1) Si existe app.lifespan.lifespan (tu versión que crea tmp/uploads, create_all, etc.)
    ls = _import_optional("app.lifespan", "lifespan")
    if ls is not None:
        return ls

    # 2) Fallback: init/close engine como en tu semana 5
    init_engine = _import_optional("app.db.base", "init_engine")
    close_engine = _import_optional("app.db.base", "close_engine")

    if init_engine or close_engine:

        @asynccontextmanager
        async def lifespan(_: FastAPI):
            if callable(init_engine):
                init_engine()  # type: ignore[misc]
            yield
            if callable(close_engine):
                close_engine()  # type: ignore[misc]

        return lifespan

    # 3) Sin lifespan
    return None


# -------------------- CORS helper --------------------
def _compute_cors() -> tuple[list[str], bool]:
    """
    Lee CORS desde settings soportando ambos nombres:
    - CORS_ORIGINS (preferido)
    - CORS_ALLOW_ORIGINS (alternativo)
    Defaults seguros en dev si está vacío.
    Endurece en producción si hay credenciales y '*' o vacío.
    """
    # Orígenes desde cualquiera de las dos claves
    origins: list[str] = []
    if hasattr(settings, "CORS_ORIGINS"):
        origins = list(getattr(settings, "CORS_ORIGINS") or [])
    elif hasattr(settings, "CORS_ALLOW_ORIGINS"):
        origins = list(getattr(settings, "CORS_ALLOW_ORIGINS") or [])

    # Normaliza
    origins = [str(o).rstrip("/") for o in origins]

    allow_credentials = bool(getattr(settings, "CORS_ALLOW_CREDENTIALS", True))
    env = str(getattr(settings, "ENV", "development")).lower()

    if allow_credentials and (not origins or "*" in origins):
        if env == "production":
            # Seguridad: exigir lista explícita en producción
            raise RuntimeError(
                "CORS_ORIGINS/CORS_ALLOW_ORIGINS no puede estar vacío ni contener '*' "
                "cuando CORS_ALLOW_CREDENTIALS=True en producción."
            )
        # Defaults de dev/preview
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://192.168.1.178:3000",
        ]

    return origins, allow_credentials


# -------------------- Routers helpers --------------------
def _safe_import_router(dotted_path: str) -> object | None:
    """
    Importa un módulo que expone 'router'. Si no existe, devuelve None.
    """
    try:
        mod = importlib.import_module(dotted_path)
        return getattr(mod, "router", None)
    except (ImportError, ModuleNotFoundError):
        return None


def _include_project_routers(app: FastAPI) -> None:
    """
    Si existe un router 'api_v1' único, úsalo. Si no, intentamos los routers sueltos.
    """
    api_v1 = _safe_import_router("app.routes.api_v1")
    if api_v1:
        app.include_router(api_v1, prefix="/api/v1")
        return

    # Fallback: routers individuales (si existen esos módulos)
    for dotted in (
        "app.routes.auth_routes",   # /api/v1/auth/...
        "app.routes.users",         # /api/v1/users...
        "app.routes.uploads",       # /api/v1/upload-csv, /api/v1/tasks/{id}
        "app.routes.processed",     # /api/v1/processed
    ):
        r = _safe_import_router(dotted)
        if r is not None:
            app.include_router(r, prefix="/api/v1")


# -------------------- Factory --------------------
def create_app() -> FastAPI:
    lifespan = _get_lifespan()

    app = FastAPI(
        title="Ops-Copilot Backend",
        version="0.1.0",
        description="Backend de práctica con FastAPI. JWT + Roles + CSV async con Celery.",
        debug=(str(getattr(settings, "ENV", "development")).lower() != "production"),
        lifespan=lifespan,  # puede ser None
    )

    # CORS
    _origins, _allow_credentials = _compute_cors()
    _env = str(getattr(settings, "ENV", "development")).lower()

    if _allow_credentials and (not _origins or "*" in _origins) and _env == "production":
        raise RuntimeError(
            "Debes definir CORS_ORIGINS/CORS_ALLOW_ORIGINS explícitos en producción."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins or ["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rutas base / debug
    @app.get("/", tags=["health"])
    def root():
        return {"hello": "world"}

    @app.get("/_debug/ping", tags=["debug"])
    def _debug_ping():
        return {"ok": True}

    @app.get("/_debug/routes", tags=["debug"])
    def _debug_routes():
        return [
            {
                "name": getattr(r, "name", None),
                "path": getattr(r, "path", None),
                "methods": sorted(list(getattr(r, "methods", set()))),
            }
            for r in app.routes
        ]

    # Routers del proyecto (si existen en app.routes.*)
    _include_project_routers(app)

    return app


# --- Alias y app global para uvicorn (app.main:app) ---
def get_app() -> FastAPI:
    """
    Crea la app principal a partir de create_app() y le añade:
    - Rate limiting global con SlowAPI
    - Routers de users y auth bajo /api/v1
    """
    app = create_app()

    # Rate limit global
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def ratelimit_handler(request, exc):
        return PlainTextResponse("Too Many Requests", status_code=429)

    # Routers que ya usabas en tu proyecto actual
    app.include_router(router, prefix="/api/v1")
    app.include_router(auth_routes.router_auth, prefix="/api/v1")
    app.include_router(auth_routes.router_login, prefix="/api/v1")

    return app


# Instancia global que Uvicorn espera: app.main:app
app = get_app()
