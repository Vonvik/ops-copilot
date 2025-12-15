import os
import sys
from typing import Dict, Any, List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from passlib.context import CryptContext

# 1) Lee DATABASE_URL (ajusta si en tu proyecto usas otro nombre de env)
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/opscopilot"

# 2) Datos del nuevo usuario (puedes sobreescribir por variables de entorno)
EMAIL = os.getenv("NEW_USER_EMAIL", "admin@test.com")
PASSWORD = os.getenv("NEW_USER_PASSWORD", "Admin123!")
FULL_NAME = os.getenv("NEW_USER_NAME", "Admin")
ROLE = os.getenv("NEW_USER_ROLE", "ADMIN")  # usa "USER" si prefieres uno normal
IS_ACTIVE = True
IS_SUPERUSER = ROLE.upper() == "ADMIN"  # por conveniencia

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_engine() -> Engine:
    return create_engine(DATABASE_URL, future=True)


def get_user_columns(conn) -> List[str]:
    # Intenta localizar la tabla users en el schema público
    cols = conn.execute(
        text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='users'
        ORDER BY ordinal_position;
        """)
    ).fetchall()
    colnames = [c[0] for c in cols]
    if not colnames:
        print("ERROR: No se encontró la tabla 'users' en el schema 'public'.")
        sys.exit(1)
    return colnames


def main():
    engine = get_engine()
    with engine.begin() as conn:
        # 0) Comprobar si ya existe el email
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email LIMIT 1"),
            {"email": EMAIL},
        ).fetchone()
        if exists:
            print(f"Ya existe un usuario con email: {EMAIL}. No se modifica.")
            return

        # 1) Descubrir columnas disponibles
        cols = get_user_columns(conn)
        # 2) Preparar payload con valores estándar y filtrar solo las columnas que existan
        payload: Dict[str, Any] = {}

        # Campos habituales (se añaden solo si existen en tu tabla)
        if "email" in cols:
            payload["email"] = EMAIL

        hashed_pw = pwd_context.hash(PASSWORD)
        # algunos proyectos usan 'hashed_password', otros 'password_hash'
        if "hashed_password" in cols:
            payload["hashed_password"] = hashed_pw
        elif "password_hash" in cols:
            payload["password_hash"] = hashed_pw

        if "full_name" in cols:
            payload["full_name"] = FULL_NAME
        if "is_active" in cols:
            payload["is_active"] = IS_ACTIVE
        if "is_superuser" in cols:
            payload["is_superuser"] = IS_SUPERUSER
        if "role" in cols:
            payload["role"] = ROLE

        # Campos opcionales comunes: username, is_verified, etc.
        if "username" in cols and "username" not in payload:
            payload["username"] = EMAIL

        if not payload:
            print("ERROR: No hay columnas compatibles para insertar. Revisa tu tabla 'users'.")
            sys.exit(1)

        # 3) Construir INSERT dinámico
        col_list = ", ".join(payload.keys())
        param_list = ", ".join([f":{k}" for k in payload.keys()])

        # ON CONFLICT si email es UNIQUE; si no lo es, se ignorará esa parte
        stmt = text(f"""
            INSERT INTO users ({col_list})
            VALUES ({param_list})
            ON CONFLICT (email) DO NOTHING
        """)

        conn.execute(stmt, payload)
        print(f"Usuario creado (o ya existente): {EMAIL}  | role={ROLE} | superuser={IS_SUPERUSER}")


if __name__ == "__main__":
    main()
