import os
import time
from collections import deque
from threading import Lock

MAX_ATTEMPTS = int(os.getenv("RATE_LIMIT_MAX_ATTEMPTS", "5"))
WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "300"))
BLOCK_SECONDS = int(os.getenv("RATE_LIMIT_BLOCK_SECONDS", "900"))


class RateLimiter:
    def __init__(self):
        self._attempts: dict[str, deque[float]] = {}
        self._blocked_until: dict[str, float] = {}
        self._lock = Lock()

    def _gc(self, key: str, now: float) -> None:
        dq = self._attempts.get(key)
        if not dq:
            return
        while dq and now - dq[0] > WINDOW:
            dq.popleft()

    def is_blocked(self, key: str, now: float | None = None) -> tuple[bool, float]:
        now = now or time.time()
        until = self._blocked_until.get(key, 0.0)
        return (now < until, max(0.0, until - now))

    def register_failure(self, key: str, now: float | None = None) -> tuple[bool, float]:
        now = now or time.time()
        with self._lock:
            blocked, remaining = self.is_blocked(key, now)
            if blocked:
                return True, remaining
            dq = self._attempts.setdefault(key, deque())
            dq.append(now)
            self._gc(key, now)
            if len(dq) > MAX_ATTEMPTS:
                self._blocked_until[key] = now + BLOCK_SECONDS
                return True, BLOCK_SECONDS
            return False, 0.0

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
            self._blocked_until.pop(key, None)


# <- EXPORTA con este nombre
rate_limiter = RateLimiter()
