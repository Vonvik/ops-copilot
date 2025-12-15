# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.db import SessionLocal
from app.models_db import User  # 👈 el modelo SQLAlchemy
from app.schemas import UserCreate, UserRead  # 👈 los nuevos esquemas

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- CREATE ---
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, name=payload.name, email=payload.email)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists") from exc
    return user


# --- READ (list all) ---
@router.get("/", response_model=list[UserRead])
def list_users(
    limit: int = 50,
    offset: int = 0,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if q:
        query = query.filter(User.name.ilike(f"%{q}%"))
    rows = query.order_by(User.id.asc()).offset(offset).limit(limit).all()
    return rows


# --- READ (single) ---
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- UPDATE ---
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserCreate, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id, name=payload.name, email=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- DELETE ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")


# Note: Returning None with a 204 status code is acceptable; FastAPI will handle it correctly.
