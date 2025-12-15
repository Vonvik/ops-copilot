# Dockerfile

# ---------- Stage 1: build de dependencias ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Paquetes del sistema necesarios para compilar dependencias (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# === Dependencias Python (pip) ===
# Copiamos solo requirements.txt para aprovechar cache de Docker
COPY requirements.txt /app/requirements.txt

# Construimos los wheels de las dependencias para usarlos en la imagen final
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r /app/requirements.txt -w /wheels


# ---------- Stage 2: imagen final ligera ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Solo dependencias de runtime (sin build-essential/gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalamos las dependencias desde los wheels construidos
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && python -m spacy download es_core_news_md


# Código de la app
COPY . /app

# Entrypoint (migraciones + uvicorn)
# (si estás en Windows, evitamos problemas de CRLF: lo normalizamos para bash)
RUN chmod +x /app/docker/entrypoint.sh && sed -i 's/\r$//' /app/docker/entrypoint.sh

EXPOSE 8000

# Usamos entrypoint fijo y un CMD por defecto ("api")
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["api"]
