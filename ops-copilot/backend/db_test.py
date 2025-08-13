import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

# Cargar .env desde la raíz del proyecto
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

dsn = os.getenv("DATABASE_URL")

def connect_via_kwargs():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="ops_copilot_dev",
        user="ops_user",
        password="LeganesNorte#28919",
    )

conn = None
try:
    if not dsn:
        print("⚠️ DATABASE_URL no definido. Usando kwargs…")
        conn = connect_via_kwargs()
    else:
        print(f"Intentando con DATABASE_URL: {dsn}")
        conn = psycopg.connect(dsn)
        print("✅ Conectado por DATABASE_URL")

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS saludos(
                  id SERIAL PRIMARY KEY,
                  mensaje TEXT NOT NULL
                )
            """)
            cur.execute("INSERT INTO saludos (mensaje) VALUES (%s)", ("Hola Postgres 👋",))

        with conn.cursor() as cur:
            cur.execute("SELECT id, mensaje FROM saludos ORDER BY id DESC LIMIT 1;")
            row = cur.fetchone()
            print("✅ Último saludo:", row)

except psycopg.OperationalError as e:
    print("❌ Error conectando con DATABASE_URL. Probando kwargs…")
    try:
        with connect_via_kwargs() as conn:
            print("✅ Conectado por kwargs (fallback)")
    except Exception as e2:
        print("❌ También falló por kwargs.")
        raise e2
