# ruff: noqa: E402
# tests/conftest.py
import os
import sys
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient

from alembic import command
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    cfg = Config("alembic.ini")
    # 🔧 Escapar % para que ConfigParser no intente interpolar
    db_url = os.environ["DATABASE_URL"].replace("%", "%%")
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


# añade la raíz del proyecto al sys.path para poder "import app"
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
