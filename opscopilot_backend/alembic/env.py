# alembic/env.py
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------- Asegurar que 'app' es importable ----------
# Carpeta raíz del repo = padre de 'alembic'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------- Config Alembic + logging ----------
alembic_config = context.config
if alembic_config and alembic_config.config_file_name:
    fileConfig(alembic_config.config_file_name)

# ---------- Importar settings / Base / modelos ----------
from app.core.config import settings  # usa tu .env
from app.db.base import Base  # Base centralizada

# ---------- Metadata objetivo ----------
target_metadata = Base.metadata


# ---------- Resolver URL de conexión ----------
def _get_database_url() -> str:
    """
    Prioridad:
      1) env var DATABASE_URL (Docker / CI)
      2) settings.DATABASE_URL
      3) alembic.ini -> sqlalchemy.url
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    if getattr(settings, "DATABASE_URL", None):
        return settings.DATABASE_URL
    return alembic_config.get_main_option("sqlalchemy.url") if alembic_config else ""

# ---------- Config común de autogenerate ----------
_common_cfg = dict(
    target_metadata=target_metadata,
    compare_type=True,
    compare_server_default=True,
    # include_schemas=True,            # activa si usas múltiples schemas
    # version_table_schema="public",   # ajusta si no usas 'public'
)


# ---------- Offline ----------
def run_migrations_offline() -> None:
    url = _get_database_url()
    context.configure(
        url=url,
        literal_binds=True,
        **_common_cfg,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------- Online ----------
def run_migrations_online() -> None:
    url = _get_database_url()
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            **_common_cfg,
        )
        with context.begin_transaction():
            context.run_migrations()


# ---------- Entrada ----------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
