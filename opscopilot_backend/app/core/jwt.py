# app/core/jwt.py
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4  # ⬅️ nuevo

from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))
RESET_SECRET = os.getenv("RESET_TOKEN_SECRET", os.getenv("SECRET_KEY", "CHANGE_ME"))
RESET_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))


def _make_token(subject: int | str, minutes: int, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "jti": str(uuid4()),  # ⬅️ ID único por token
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: int | str, expires_minutes: int | None = None) -> str:
    return _make_token(subject, expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES, "access")


def create_refresh_token(subject: int | str, expires_minutes: int | None = None) -> str:
    return _make_token(subject, expires_minutes or REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def create_reset_token(email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email.lower(),
        "type": "password_reset",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=RESET_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, RESET_SECRET, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, RESET_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
