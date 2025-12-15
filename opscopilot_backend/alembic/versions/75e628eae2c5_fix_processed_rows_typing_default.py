"""fix processed_rows typing/default

Revision ID: 75e628eae2c5
Revises: b28800d0a4f7
Create Date: 2025-10-12 13:49:39.247160

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "75e628eae2c5"
down_revision: str | Sequence[str] | None = "b28800d0a4f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
