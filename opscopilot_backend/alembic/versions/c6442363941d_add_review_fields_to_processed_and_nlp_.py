"""add review fields to processed_rows and nlp_extractions

Revision ID: c6442363941d
Revises: 3df654048a6b
Create Date: 2025-10-22 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c6442363941d"
down_revision: str | Sequence[str] | None = "3df654048a6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Añadir campos de revisión y confianza a processed_rows y nlp_extractions."""

    # Antes apuntaba a la tabla inexistente "processed";
    # aquí usamos el nombre real "processed_rows"
    op.add_column(
        "processed_rows",
        sa.Column("nlp_overall_confidence", sa.Float(), nullable=True),
    )
    op.add_column(
        "processed_rows",
        sa.Column(
            "needs_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Campo de estado de revisión en las extracciones NLP
    op.add_column(
        "nlp_extractions",
        sa.Column("review_status", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    """Revertir campos añadidos en esta revisión."""
    op.drop_column("nlp_extractions", "review_status")
    op.drop_column("processed_rows", "needs_review")
    op.drop_column("processed_rows", "nlp_overall_confidence")
