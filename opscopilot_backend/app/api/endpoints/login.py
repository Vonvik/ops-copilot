# app/api/v1/endpoints/login.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()

# Usuario de prueba (desarrollo)
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASS  = "Admin123!"

class UserPublic(BaseModel):
    id: int | None = 1
    email: str
    role: str = "ADMIN"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic | None = None

# Login estilo OAuth2PasswordRequestForm (username/password)
@router.post("/access-token", response_model=TokenResponse, tags=["login"])
def login_access_token(form: OAuth2PasswordRequestForm = Depends()):
    # En tu backend real, valida contra BD
    if form.username != ADMIN_EMAIL or form.password != ADMIN_PASS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Token de desarrollo (dummy). En producción, genera un JWT real.
    token = "dev-dummy-token"

    return TokenResponse(
        access_token=token,
        user=UserPublic(email=ADMIN_EMAIL, role="ADMIN")
    )

# End-point para devolver el usuario actual (usa el token dev)
@router.get("/me", response_model=UserPublic, tags=["users"])
def users_me(authorization: str | None = None):
    # Espera: Authorization: Bearer dev-dummy-token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    if token != "dev-dummy-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return UserPublic(email=ADMIN_EMAIL, role="ADMIN")
