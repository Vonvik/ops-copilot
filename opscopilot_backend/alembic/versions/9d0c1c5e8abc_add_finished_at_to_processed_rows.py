"""add finished_at to processed_rows

Revision ID: 9d0c1c5e8abc
Revises: 5d12f050fb3e
Create Date: 2025-12-13
"""

from alembic import op
import sqlalchemy as sa

# IDs de Alembic
revision = "9d0c1c5e8abc"
down_revision = "5d12f050fb3e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Añadimos la columna finished_at si no existe aún
    op.add_column(
        "processed_rows",
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("processed_rows", "finished_at")
