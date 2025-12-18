"""merge heads

Revision ID: 421bf395f0ea
Revises: REPLACE_ME, ed15603b0185
Create Date: 2025-12-18 17:31:42.046213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '421bf395f0ea'
down_revision: Union[str, Sequence[str], None] = ('REPLACE_ME', 'ed15603b0185')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
