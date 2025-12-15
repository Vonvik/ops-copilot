"""init

Revision ID: 831a057075e1
Revises: ebde90037161
Create Date: 2025-10-19 18:33:38.109659

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "831a057075e1"
down_revision: str | Sequence[str] | None = "ebde90037161"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
