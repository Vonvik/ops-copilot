# app/core/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

# =========================
# Config
# =========================
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Access token
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")  # ⬅️ cámbialo en producción
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

# Refresh token (puede ser otro secreto distinto)
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET", SECRET_KEY)
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 días

# Password reset token
RESET_TOKEN_SECRET = os.getenv("RESET_TOKEN_SECRET", SECRET_KEY)
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))

RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
PASSWORD_RESET_SECRET = os.getenv("PASSWORD_RESET_SECRET", os.getenv("JWT_SECRET_KEY", "change-me"))
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# Password helpers
# =========================
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# JWT helpers
# =========================
def _create_token(
    subject: str | int,
    *,
    minutes: int,
    secret: str,
    token_type: str,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def create_access_token(subject: str | int) -> str:
    return _create_token(
        subject,
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        secret=SECRET_KEY,
        token_type="access",
    )


def create_refresh_token(subject: str | int) -> str:
    return _create_token(
        subject,
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
        secret=REFRESH_TOKEN_SECRET,
        token_type="refresh",
    )


def verify_token(token: str, *, expected_type: str, secret: str) -> dict[str, Any] | None:
    """
    Verifica y devuelve el payload si es válido y de tipo esperado; si no, None.
    """
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None


# =========================
# Password reset tokens
# =========================
def create_reset_token(email: str) -> str:
    # el "sub" del reset será el email normalizado (lower)
    return _create_token(
        email.lower(),
        minutes=RESET_TOKEN_EXPIRE_MINUTES,
        secret=RESET_TOKEN_SECRET,
        token_type="password_reset",
    )


def verify_reset_token(token: str) -> str | None:
    payload = verify_token(token, expected_type="password_reset", secret=RESET_TOKEN_SECRET)
    if not payload:
        return None
    return payload.get("sub")  # email


def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "type": "reset", "exp": expire}
    return jwt.encode(to_encode, PASSWORD_RESET_SECRET, algorithm=JWT_ALG)


def verify_password_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, PASSWORD_RESET_SECRET, algorithms=[JWT_ALG])
        if payload.get("type") != "reset":
            return None
        return payload.get("sub")  # email
    except JWTError:
        return None
