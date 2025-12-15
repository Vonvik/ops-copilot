# tools/fix_alembic_stamp.py
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, future=True)

SQL_UPDATE = text("UPDATE alembic_version SET version_num=:v")
SQL_EXISTS = text("SELECT to_regclass('public.alembic_version')")
SQL_CREATE = text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
SQL_COUNT = text("SELECT COUNT(*) FROM alembic_version")
SQL_DELETE = text("DELETE FROM alembic_version")
SQL_INSERT = text("INSERT INTO alembic_version (version_num) VALUES (:v)")

TARGET = "831a057075e1"

with engine.begin() as conn:
    # crea tabla si no existe
    res = conn.execute(SQL_EXISTS).scalar()
    if res is None:
        conn.execute(SQL_CREATE)

    try:
        upd = conn.execute(SQL_UPDATE, {"v": TARGET})
        if upd.rowcount == 0:
            # no había fila -> insert controlado
            cnt = conn.execute(SQL_COUNT).scalar()
            if cnt and cnt > 0:
                conn.execute(SQL_DELETE)
            conn.execute(SQL_INSERT, {"v": TARGET})
    except SQLAlchemyError:
        # último recurso: delete+insert
        conn.execute(SQL_DELETE)
        conn.execute(SQL_INSERT, {"v": TARGET})
        conn.execute(SQL_INSERT, {"v": TARGET})

print("Stamped DB to", TARGET)
