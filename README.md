# OpsCopilot

OpsCopilot es una aplicación web que automatiza la captura y estructuración de registros (p. ej. gastos), con flujo de revisión y panel de control.

## Requisitos
- Docker Desktop (Windows/Mac) o Docker Engine (Linux)

## Arranque rápido (Docker)
1) Crea tu fichero de variables:
   - Copia `.env.example` a `.env`
   - Ajusta valores si lo necesitas (especialmente `NEXTAUTH_SECRET` y `SECRET_KEY`)

2) Levanta todo el stack:
```bash
docker compose up -d --build
