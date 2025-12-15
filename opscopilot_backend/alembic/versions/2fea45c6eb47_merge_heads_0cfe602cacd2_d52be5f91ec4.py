"""merge heads 0cfe602cacd2 + d52be5f91ec4

Revision ID: 2fea45c6eb47
Revises: 0cfe602cacd2, d52be5f91ec4
Create Date: 2025-10-11 11:59:00.803402

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2fea45c6eb47"
down_revision: str | Sequence[str] | None = ("0cfe602cacd2", "d52be5f91ec4")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
