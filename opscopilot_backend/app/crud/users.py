from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(
        email=user_in.email.lower(),
        full_name=user_in.full_name,
        role=user_in.role or "user",
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email.lower())
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_password(db: Session, user: User, new_hashed: str) -> User:
    user.hashed_password = new_hashed
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
