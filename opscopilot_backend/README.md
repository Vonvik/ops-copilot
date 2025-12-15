# 🚀 Ops-Copilot Backend

**Ops-Copilot** es la capa backend del ecosistema Ops-Copilot, diseñada para automatizar procesos y consolidar datos empresariales de forma inteligente.

Construida con **FastAPI**, **PostgreSQL** y **SQLAlchemy**, ofrece una API escalable, segura y preparada para integrarse con paneles de control, aplicaciones web y servicios de IA.

---

## ⚙️ Arquitectura
- **FastAPI** – Framework backend asíncrono y de alto rendimiento.
- **SQLAlchemy 2.x** – ORM moderno con tipado y soporte nativo para Postgres.
- **Alembic** – Control de versiones y migraciones de base de datos.
- **Pydantic v2** – Validación y serialización avanzada.
- **Uvicorn** – Servidor ASGI para despliegue productivo.

---

## 🧩 Estructura del proyecto
OpsCopilot_backend/
│
├── app/
│ ├── main.py → Punto de entrada FastAPI
│ ├── db.py → Conexión y sesión SQLAlchemy
│ ├── models_db.py → Modelos de base de datos
│ ├── crud.py → Operaciones CRUD
│ ├── schemas.py → Validaciones Pydantic
│ └── routes/ → Endpoints REST (users, items, etc.)
│
├── alembic/ → Migraciones de base de datos
├── alembic.ini
├── requirements.txt
└── README.md

---

## 🛠️ Instalación
bash
python -m venv venv
venv\Scripts\activate        # En Windows
# source venv/bin/activate   # En Mac/Linux
pip install -r requirements.txt
🔑 Configuración del entorno
Crea un archivo .env en la raíz con tu URL de conexión a base de datos:

bash

DATABASE_URL=postgresql+psycopg2://usuario:contraseña@localhost/ops_copilot_dev
⚠️ No subas este archivo al repositorio.
Usa variables de entorno en servidores productivos (Docker, Render, etc.).

🧱 Migraciones de base de datos
bash

alembic revision --autogenerate -m "init"
alembic upgrade head
Cada vez que cambies tus modelos:

bash

alembic revision --autogenerate -m "mensaje"
alembic upgrade head
▶️ Ejecutar servidor local
bash

uvicorn app.main:app --reload
Documentación interactiva:
👉 http://127.0.0.1:8000/docs

📡 Endpoints principales
Users
Método	Endpoint	Descripción
POST	/api/v1/users/	Crear usuario
GET	/api/v1/users/	Listar usuarios (paginado)
GET	/api/v1/users/{id}	Obtener usuario
PUT	/api/v1/users/{id}	Actualizar usuario
DELETE	/api/v1/users/{id}	Eliminar usuario

🔒 Seguridad (próximas versiones)
Autenticación JWT

Encriptación de contraseñas con bcrypt

Roles y permisos (Admin / User)

Protección CORS y cabeceras seguras

📦 Despliegue (planeado)
Contenedores Docker (app + PostgreSQL)

Variables de entorno gestionadas

CI/CD para automatizar migraciones y test

🧠 Visión
Ops-Copilot evoluciona hacia una plataforma de automatización modular y escalable, con integración IA, dashboards y gestión multiusuario.

🧰 Dependencias principales
ini

fastapi==0.115.0
uvicorn==0.30.1
sqlalchemy==2.0.34
psycopg2-binary==2.9.9
python-dotenv==1.0.1
alembic==1.13.2
pydantic==2.9.2
pydantic-settings==2.5.2

👤 Autor: Victor Lobete

