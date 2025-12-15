# app/rate_limiter.py
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # Accedemos a request y exc para evitar los warnings y dar contexto útil
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Try again later.",
            "path": request.url.path,
            "method": request.method,
            "client": (request.client.host if request.client else None),
            "error": str(exc),
        },
        headers={"Retry-After": "60"},  # opcional
    )
