# app/lifespan.py
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.__init__ import Base, engine


@asynccontextmanager
async def lifespan(app):
    uploads_dir = Path("tmp/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[lifespan] ✅ startup (db_ok=True, uploads_dir='{uploads_dir}')")
    except SQLAlchemyError as e:
        print(f"[lifespan] ⚠️ startup (db_ok=False): {e!r}")

    yield
    print("[lifespan] 🔻 shutdown")
