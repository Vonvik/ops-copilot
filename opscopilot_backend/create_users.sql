CREATE TABLE IF NOT EXISTS public.users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(320) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name       VARCHAR(256),
    role            VARCHAR(32) NOT NULL DEFAULT 'USER',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_users_email ON public.users (email);