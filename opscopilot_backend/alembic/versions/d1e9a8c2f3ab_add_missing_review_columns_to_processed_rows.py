"""add missing review columns to processed_rows

Revision ID: d1e9a8c2f3ab
Revises: b7a3c23b4d10
Create Date: 2025-12-18

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d1e9a8c2f3ab"
down_revision: str | Sequence[str] | None = "b7a3c23b4d10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Añadimos columnas que el backend ya usa.
    # IMPORTANTE: NO creamos FK aquí para no fallar si la tabla `users` no existe aún en esa DB.
    op.add_column("processed_rows", sa.Column("review_status", sa.String(length=20), nullable=True))
    op.add_column("processed_rows", sa.Column("reviewed_by_id", sa.Integer(), nullable=True))
    op.add_column("processed_rows", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("processed_rows", "reviewed_at")
    op.drop_column("processed_rows", "reviewed_by_id")
    op.drop_column("processed_rows", "review_status")
