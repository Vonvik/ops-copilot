"""align users model to sqlalchemy2 typing

Revision ID: b5865ec14df6
Revises: aa9e06279680
Create Date: 2025-10-12 14:33:12.391187

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5865ec14df6"
down_revision: str | Sequence[str] | None = "aa9e06279680"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
