#!/usr/bin/env bash
set -e

# Info rápida de conexión a BD (debug)
if [ -n "${DATABASE_URL}" ]; then
  echo ">> DATABASE_URL: ${DATABASE_URL}"
fi

wait_for_db() {
  echo ">> Esperando a que Postgres esté listo..."
  python - <<'PY'
import os, time, re
import psycopg2

db_url = os.environ.get("DATABASE_URL", "")
if not db_url:
    raise SystemExit("DATABASE_URL no está definido")

# psycopg2 no entiende el esquema "postgresql+psycopg2"
dsn = re.sub(r"^postgresql\+psycopg2://", "postgresql://", db_url)

max_attempts = int(os.environ.get("DB_MAX_ATTEMPTS", "30"))
sleep_seconds = float(os.environ.get("DB_SLEEP_SECONDS", "1"))

last_err = None
for i in range(1, max_attempts + 1):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        print(f">> Postgres OK (intento {i}/{max_attempts})")
        raise SystemExit(0)
    except Exception as e:
        last_err = e
        print(f">> Postgres no listo (intento {i}/{max_attempts}): {e}")
        time.sleep(sleep_seconds)

print(f">> ERROR: Postgres no respondió tras {max_attempts} intentos. Último error: {last_err}")
raise SystemExit(1)
PY
}

# Modo por defecto: API (backend HTTP)
if [ "$1" = "api" ] || [ -z "$1" ]; then
  wait_for_db

  echo ">> Ejecutando migraciones Alembic..."
  alembic upgrade head

  echo ">> Arrancando API con Uvicorn..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
  # Para otros comandos (por ejemplo, worker de Celery),
  # simplemente ejecutamos lo que nos pasen.
  echo ">> Ejecutando comando personalizado: $@"
  exec "$@"
fi
