"""add user_id to processed_rows

Revision ID: b7a3c23b4d10
Revises: 9d0c1c5e8abc
Create Date: 2025-12-13
"""

from alembic import op
import sqlalchemy as sa

# IDs de Alembic
revision = "b7a3c23b4d10"
down_revision = "9d0c1c5e8abc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Añadimos la columna user_id si no existe aún
    op.add_column(
        "processed_rows",
        sa.Column("user_id", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("processed_rows", "user_id")
