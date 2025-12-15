# app/api/routes/auth.py
import os
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# Seguridad / helpers existentes
from app.api.deps_rate_limit import ensure_not_blocked
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.rate_limit import rate_limiter  # in-memory attempts (propio)
from app.core.ratelimit import limiter        # SlowAPI Limiter (global)
from app.core.security import (
    create_password_reset_token,
    verify_password_reset_token,
)
from app.crud.users import (
    authenticate,
    create_user,
    get_user_by_email,
    set_user_password,
)
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordIn,
    PasswordResetConfirm,
    RefreshTokenIn,
    Token,
)
from app.schemas.user import UserCreate, UserRead
from app.services.email import send_password_reset

# ---------------------------------------------------------------------------
# Routers:
#   - router_auth  -> prefijo "/auth"  (signup, login JSON/FORM unificado, refresh, logout, forgot, reset, sync_oauth)
#   - router_login -> prefijo "/login" (compatibilidad OAuth2: /login/access-token y /login/me)
# Se montan en main.py con prefix="/api/v1".
# ---------------------------------------------------------------------------

router_auth = APIRouter(prefix="/auth", tags=["auth"])
router_login = APIRouter(prefix="/login", tags=["login"])  # compat OAuth2

SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"


def _set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200")) * 60,
        path="/",
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(key="refresh_token", path="/")


# --------- Schemas auxiliares ----------
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class SyncIn(BaseModel):
    email: EmailStr


# ==========================
#   AUTH (prefijo /auth)
# ==========================

@router_auth.post("/signup", response_model=UserRead, status_code=201)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        return create_user(db, user_in)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc


@router_auth.post("/login", response_model=Token)
@limiter.limit("5/minute")  # 5 intentos por IP/minuto (SlowAPI)
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Acepta:
      - application/json: {"email": "...", "password": "..."}
      - application/x-www-form-urlencoded: username=...&password=...
    Emite: access_token (JWT) y set-cookie con refresh_token (httponly).
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        email = (data or {}).get("email")
        password = (data or {}).get("password")
    else:
        form = await request.form()
        email = form.get("username")  # OAuth2PasswordRequestForm usa 'username'
        password = form.get("password")

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing credentials")

    # Rate-limit por IP+email (contador propio en memoria)
    key = ensure_not_blocked(request, email)

    # Autenticar contra tu BD real
    user = authenticate(db, email, password)
    if not user:
        blocked, retry_after = rate_limiter.register_failure(key)
        if blocked:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Try again later.",
                headers={"Retry-After": str(int(retry_after))},
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        blocked, retry_after = rate_limiter.register_failure(key)
        if blocked:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Try again later.",
                headers={"Retry-After": str(int(retry_after))},
            )
        raise HTTPException(status_code=400, detail="Inactive user")

    # Éxito → limpiar contador
    rate_limiter.reset(key)

    # Emitir tokens (JWT reales de tu core.jwt)
    access = create_access_token(subject=user.id)
    refresh = create_refresh_token(subject=user.id)
    _set_refresh_cookie(response, refresh)

    return Token(access_token=access)


@router_auth.post("/refresh", response_model=Token)
def refresh_token(
    response: Response,
    body: RefreshTokenIn | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    db: Session = Depends(get_db),
):
    token = refresh_cookie or (body.refresh_token if body else None)
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload.get("sub", "0"))
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Rotación
    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)
    _set_refresh_cookie(response, new_refresh)
    return Token(access_token=new_access)


@router_auth.post("/logout")
def logout(response: Response):
    _clear_refresh_cookie(response)
    return {"detail": "Logged out"}


@router_auth.post("/forgot-password", status_code=200)
def forgot_password(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    """
    Siempre responde 200. Solo genera y envía el token si el usuario existe.
    """
    user = get_user_by_email(db, body.email)
    if user:
        token = create_password_reset_token(user.email)
        send_password_reset(user.email, token)
    return {"message": "If the email exists, a reset link was sent."}


@router_auth.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(body: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Verifica token → respuesta genérica (no filtra si el usuario existe o está activo).
    """
    email = verify_password_reset_token(body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        # Respuesta idéntica para no filtrar información
        return {"message": "Password updated"}

    set_user_password(db, user, body.new_password)
    return {"message": "Password updated"}


@router_auth.post("/sync_oauth")
def sync_oauth(body: SyncIn, db: Session = Depends(get_db)):
    """
    Devuelve el rol de un usuario por email (para vincular cuentas OAuth en el frontend).
    """
    user = get_user_by_email(db, body.email)
    role = getattr(user, "role", None) or "USER"
    return {"role": role}


# ==========================
#   LOGIN compat (/login)
# ==========================

# NOTA: este shim es para NextAuth Credentials.
# Usa credenciales fijas en dev; puedes cambiarlo luego a BD real.

ADMIN_EMAIL = "admin@test.com"
ADMIN_PASS = "Admin123!"


class UserPublic(BaseModel):
    id: int = 1
    email: str
    role: str = "ADMIN"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


@router_login.post("/access-token", response_model=TokenResponse)
def login_access_token(form: OAuth2PasswordRequestForm = Depends()):
    """
    Compatibilidad OAuth2PasswordRequestForm (x-www-form-urlencoded).
    Ruta final: /api/v1/login/access-token
    Usado por NextAuth Credentials.
    """
    # En producción, aquí deberías usar authenticate()/DB, igual que /auth/login.
    if form.username != ADMIN_EMAIL or form.password != ADMIN_PASS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(
        access_token="dev-dummy-token",
        user=UserPublic(email=ADMIN_EMAIL, role="ADMIN"),
    )


@router_login.get("/me", response_model=UserPublic)
def login_me(authorization: str | None = None):
    """
    Compat de /login/me para completar user info con token dummy.
    Ruta final: /api/v1/login/me
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    if token != "dev-dummy-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return UserPublic(email=ADMIN_EMAIL, role="ADMIN")
