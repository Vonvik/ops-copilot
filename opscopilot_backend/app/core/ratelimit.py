# app/core/ratelimit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# Por defecto, usa memoria; para Redis: Limiter(key_func=get_remote_address, storage_uri="redis://127.0.0.1:6379")
limiter = Limiter(key_func=get_remote_address)
