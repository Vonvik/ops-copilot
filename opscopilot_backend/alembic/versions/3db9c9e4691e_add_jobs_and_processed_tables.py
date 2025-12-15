"""add jobs and processed tables

Revision ID: 3db9c9e4691e
Revises: dd0fa6f1ba90
Create Date: 2025-10-20 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3db9c9e4691e"
down_revision: str | Sequence[str] | None = "dd0fa6f1ba90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: crear tablas jobs y processed_rows (versión final)."""

    # --- Limpieza defensiva de restos antiguos ---
    # No intentamos borrar índices sueltos; si existen tablas, se borran con CASCADE
    op.execute(sa.text("DROP TABLE IF EXISTS processed_rows CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS jobs CASCADE;"))

    # --- Tabla jobs ---
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # --- Tabla processed_rows (versión actual del modelo) ---
    op.create_table(
        "processed_rows",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("item", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("date_str", sa.String(length=50), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # Índices actuales
    op.create_index("ix_processed_rows_id", "processed_rows", ["id"], unique=False)
    op.create_index("ix_processed_rows_item", "processed_rows", ["item"], unique=False)


def downgrade() -> None:
    """Downgrade schema: eliminar tablas creadas en esta revisión."""
    # Simétrico: borramos tablas; los índices caen en cascada
    op.execute(sa.text("DROP TABLE IF EXISTS processed_rows CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS jobs CASCADE;"))
