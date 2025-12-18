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
    # processed_rows: faltaban columnas que el backend ya está usando
    op.add_column("processed_rows", sa.Column("review_status", sa.String(length=20), nullable=True))  # type: ignore[attr-defined]
    op.add_column("processed_rows", sa.Column("reviewed_by_id", sa.Integer(), nullable=True))  # type: ignore[attr-defined]
    op.add_column("processed_rows", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))  # type: ignore[attr-defined]

    # FK opcional (recomendado): quién revisó (users.id)
    op.create_foreign_key(  # type: ignore[attr-defined]
        "fk_processed_rows_reviewed_by_id_users",
        "processed_rows",
        "users",
        ["reviewed_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_processed_rows_reviewed_by_id_users", "processed_rows", type_="foreignkey")  # type: ignore[attr-defined]
    op.drop_column("processed_rows", "reviewed_at")  # type: ignore[attr-defined]
    op.drop_column("processed_rows", "reviewed_by_id")  # type: ignore[attr-defined]
    op.drop_column("processed_rows", "review_status")  # type: ignore[attr-defined]
