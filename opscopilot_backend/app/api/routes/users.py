from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.endpoints import login, nlp
from app.api.deps import get_current_active_user, require_roles
from app.db import get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(login.router, prefix="/login", tags=["login"])
router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),  # solo admins
):
    return db.query(User).all()
