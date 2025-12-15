# app/openapi.py
tags_metadata = [
    {
        "name": "auth",
        "description": "Autenticación y autorización (login, registro, JWT).",
    },
    {"name": "users", "description": "Gestión de usuarios y perfiles."},
    {
        "name": "uploads",
        "description": "Subida de CSV y encolado de tareas con Celery.",
    },
    {"name": "processed", "description": "Lectura de filas procesadas desde la BD."},
]
