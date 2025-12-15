"""fix user model typing

Revision ID: ebde90037161
Revises: b5865ec14df6
Create Date: 2025-10-12 14:34:39.600489

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebde90037161"
down_revision: str | Sequence[str] | None = "b5865ec14df6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
