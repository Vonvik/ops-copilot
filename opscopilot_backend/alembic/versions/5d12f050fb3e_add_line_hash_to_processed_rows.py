"""add line_hash to processed_rows

Revision ID: 5d12f050fb3e
Revises: c6442363941d
Create Date: 2025-12-13

"""
from alembic import op
import sqlalchemy as sa

# IDs de Alembic
revision = "5d12f050fb3e"
down_revision = "c6442363941d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Añadimos la columna line_hash si no existe aún
    op.add_column(
        "processed_rows",
        sa.Column("line_hash", sa.String(length=64), nullable=False, server_default=""),
    )
    op.create_index(
        op.f("ix_processed_rows_line_hash"),
        "processed_rows",
        ["line_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_processed_rows_line_hash"), table_name="processed_rows")
    op.drop_column("processed_rows", "line_hash")
