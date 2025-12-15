import logging
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
logger = logging.getLogger(__name__)


def send_password_reset(email: str, token: str) -> None:
    """
    Placeholder simple para reset de contraseña.
    En producción se enviaría un email real.
    """
    print(f"[send_password_reset] Reset token for {email}: {token}")
