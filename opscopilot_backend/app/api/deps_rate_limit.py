from fastapi import HTTPException, Request
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.rate_limit import rate_limiter


def login_rate_key(request: Request, username: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{host}:{username.lower()}"


def ensure_not_blocked(request: Request, username: str) -> str:
    key = login_rate_key(request, username)
    blocked, retry_after = rate_limiter.is_blocked(key)
    if blocked:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again later.",
            headers={"Retry-After": str(int(retry_after))},
        )
    return key
