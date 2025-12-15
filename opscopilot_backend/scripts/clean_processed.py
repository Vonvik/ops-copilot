# scripts/clean_processed.py
from sqlalchemy import text

from app.db.__init__ import engine  # usa el mismo engine que la API (carga .env)

with engine.begin() as conn:
    conn.execute(text("DELETE FROM processed_rows"))
print("clean done")
