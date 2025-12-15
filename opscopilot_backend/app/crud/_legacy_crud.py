from sqlalchemy.orm import Session

from app.models._legacy_models_db import User


def create_user(db: Session, name: str, email: str):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, name: str | None = None, email: str | None = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if name:
        user.name = name
    if email:
        user.email = email
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
