# tests/test_auth.py
def test_signup_and_login(client):
    # signup (201 si nuevo, 409 si ya existía)
    r = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "full_name": "Tester",
            "role": "user",
            "password": "Secret1234",
        },
    )
    assert r.status_code in (200, 201, 409)

    # login
    r2 = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "Secret1234"},
    )
    assert r2.status_code == 200
    token = r2.json()["access_token"]

    # ruta protegida
    r3 = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200


def test_login_bad_password(client):
    # usuario existe de pruebas previas
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "WrongPass123"},
    )
    assert r.status_code == 401


def test_admin_only_route_for_user_role(client):
    # signup usuario normal
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "plainuser@example.com",
            "full_name": "Plain User",
            "role": "user",
            "password": "UserSecret123",
        },
    )
    # login
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "plainuser@example.com", "password": "UserSecret123"},
    )
    token = r.json()["access_token"]
    # intento a /users (debe ser 403)
    r2 = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


def test_signup_duplicate_email_returns_409(client):
    email = "dup@example.com"
    body = {
        "email": email,
        "full_name": "Dup",
        "role": "user",
        "password": "Secret1234",
    }
    r1 = client.post("/api/v1/auth/signup", json=body)
    assert r1.status_code in (200, 201, 409)
    r2 = client.post("/api/v1/auth/signup", json=body)
    assert r2.status_code == 409


def test_refresh_and_logout_flow(client):
    # signup
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "refresh@example.com",
            "full_name": "Refresh",
            "role": "user",
            "password": "Secret1234",
        },
    )

    # login
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "Secret1234"},
    )
    assert r.status_code == 200
    access1 = r.json()["access_token"]

    # refresh usando body (Swagger-like)
    # ojo: TestClient no mantiene cookies por defecto entre llamadas si se recrea, pero aquí es la misma instancia
    # así que también funcionaría sin body. Para ser explícitos:
    # extraemos la cookie de la respuesta de login
    refresh_cookie = r.cookies.get("refresh_token")
    assert refresh_cookie

    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_cookie})
    assert r2.status_code == 200
    access2 = r2.json()["access_token"]
    assert access2 != access1  # debería rotar

    # logout
    r3 = client.post("/api/v1/auth/logout")
    assert r3.status_code == 200

    # refresh después de logout (si mandamos el body seguirá valiendo porque no hay denylist)
    # pero SIN body (solo cookie) debería fallar porque se borró la cookie:
    r4 = client.post("/api/v1/auth/refresh")
    assert r4.status_code == 401
