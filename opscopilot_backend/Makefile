# ====== Makefile cross-platform (Windows CMD / Unix) ======

# Detectar Windows
ifeq ($(OS),Windows_NT)
  # En Windows usamos cmd.exe
  SHELL := cmd.exe
  .SHELLFLAGS := /C
  # Prefijo para exportar DATABASE_URL en una sola línea
  SETENV = set "DATABASE_URL=$(DB_URL)" &&
  # Comprobación del mensaje para revision
  CHECK_MSG = if "$(m)"=="" ( echo ❌ Falta el mensaje: make revision m="create users" & exit /b 1 )
else
  # Unix (bash/sh)
  SHELL := /bin/sh
  .SHELLFLAGS := -c
  SETENV =
  CHECK_MSG = if [ -z "$(m)" ]; then echo "❌ Falta el mensaje: make revision m='create users'"; exit 1; fi
endif

# -------- Config básica --------
PY        ?= python
PIP       ?= pip
UVICORN   ?= uvicorn
APP_PATH  ?= app.main:create_app     # usamos la factory create_app con --factory

# Si no defines DB_URL en tu entorno, usamos esta por defecto (local)
DB_URL ?= postgresql+psycopg2://postgres:postgres@localhost:5432/ops_copilot_dev

# -------- Utilidades --------
.PHONY: help venv install run test lint fmt revision migrate downgrade alembic-current alembic-history \
        docker-up docker-build docker-logs docker-down docker-sh migrate-in-docker

help:
	@echo Comandos utiles:
	@echo   make install            -> instalar deps \(requirements.txt\)
	@echo   make run                -> arrancar API \(uvicorn --reload\)
	@echo   make test               -> ejecutar pytest
	@echo   make lint               -> ruff check
	@echo   make fmt                -> ruff format
	@echo   make revision m='msg'   -> alembic revision --autogenerate -m 'msg'
	@echo   make migrate            -> alembic upgrade head
	@echo   make downgrade          -> alembic downgrade -1
	@echo   make alembic-current    -> alembic current
	@echo   make alembic-history    -> alembic history
	@echo   make docker-up          -> docker compose up -d \(build si hace falta\)
	@echo   make docker-build       -> docker compose up --build -d
	@echo   make docker-logs        -> logs del contenedor api
	@echo   make docker-down        -> docker compose down -v
	@echo   make docker-sh          -> shell dentro del contenedor api
	@echo   make migrate-in-docker  -> alembic upgrade head dentro del contenedor api

# -------- Entorno / deps --------
venv:
	$(PY) -m venv .venv

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# -------- Desarrollo local --------
run:
	$(UVICORN) $(APP_PATH) --factory --reload --host 0.0.0.0 --port 8000

test:
	$(SETENV) pytest -q

lint:
	ruff check .

fmt:
	ruff format .

# -------- Alembic --------
revision:
	$(CHECK_MSG)
	$(SETENV) alembic revision --autogenerate -m "$(m)"

migrate:
	$(SETENV) alembic upgrade head

downgrade:
	$(SETENV) alembic downgrade -1

alembic-current:
	$(SETENV) alembic current

alembic-history:
	$(SETENV) alembic history

# -------- Docker helpers --------
docker-up:
	docker compose up -d

docker-build:
	docker compose up --build -d

docker-logs:
	docker compose logs -f api

docker-down:
	docker compose down -v

docker-sh:
	docker compose exec api bash

# Si tu contenedor ya tiene DATABASE_URL con compose/.env, no hace falta inyectarla aquí.
migrate-in-docker:
	docker compose exec api alembic upgrade head
