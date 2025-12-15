"""fix processed_rows.created_at default

Revision ID: b28800d0a4f7
Revises: 2fea45c6eb47
Create Date: 2025-10-12 12:22:25.545216

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b28800d0a4f7"
down_revision: str | Sequence[str] | None = "2fea45c6eb47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
