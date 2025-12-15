from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from collections.abc import Generator
from app.core.config import settings

_engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass


def init_engine():
    global _engine, SessionLocal
    if _engine is None:
        _engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine():
    return _engine


def get_session():
    if SessionLocal is None:
        init_engine()
    return SessionLocal()


def close_engine():
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
def get_db() -> Generator[Session, None, None]:
    """
    Dependency para FastAPI.
    Abre una sesión por petición y la cierra siempre al final.
    """
    db = get_session()  # reutilizamos tu helper existente
    try:
        yield db
    finally:
        db.close()