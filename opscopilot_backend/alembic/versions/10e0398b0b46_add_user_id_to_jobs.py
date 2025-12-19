"""add user_id to jobs

Revision ID: 10e0398b0b46
Revises: 421bf395f0ea
Create Date: 2025-12-18 21:36:13.838796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10e0398b0b46'
down_revision: Union[str, Sequence[str], None] = '421bf395f0ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("user_id", sa.String(length=50), nullable=True))
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_jobs_user_id", table_name="jobs")
    op.drop_column("jobs", "user_id")
