"""add nlp_extractions table

Revision ID: 3df654048a6b
Revises: 3db9c9e4691e
Create Date: 2025-10-21 00:00:00.000000
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3df654048a6b"
down_revision: str | Sequence[str] | None = "3db9c9e4691e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear tabla nlp_extractions básica, enganchada a jobs."""
    op.create_table(
        "nlp_extractions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
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

    # Índices sencillos
    op.create_index(
        "ix_nlp_extractions_id",
        "nlp_extractions",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_nlp_extractions_item",
        "nlp_extractions",
        ["item"],
        unique=False,
    )


def downgrade() -> None:
    """Eliminar tabla nlp_extractions e índices."""
    op.drop_index("ix_nlp_extractions_item", table_name="nlp_extractions")
    op.drop_index("ix_nlp_extractions_id", table_name="nlp_extractions")
    op.drop_table("nlp_extractions")
