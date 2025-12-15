"""add users table

Revision ID: aa9e06279680
Revises: 75e628eae2c5
Create Date: 2025-10-12 14:20:35.308975

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa9e06279680"
down_revision: str | Sequence[str] | None = "75e628eae2c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
