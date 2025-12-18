"""add filename column to jobs

Revision ID: ed15603b0185
Revises: d1e9a8c2f3ab
Create Date: 2025-12-18 16:22:28.337507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed15603b0185'
down_revision: Union[str, Sequence[str], None] = 'd1e9a8c2f3ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # En Postgres: idempotente (si ya existe, no falla)
    op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS filename TEXT;")

def downgrade() -> None:
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS filename;")