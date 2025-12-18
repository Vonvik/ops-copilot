from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "REPLACE_ME"
down_revision: str | Sequence[str] | None = "d1e9a8c2f3ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Como estamos en etapa temprana y no hay datos importantes:
    # reconstruimos tablas para alinear DB con el modelo actual.
    op.execute(sa.text("DROP TABLE IF EXISTS nlp_extractions CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS processed_rows CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS jobs CASCADE;"))

    # JOBS (alineado con lo que usa el endpoint upload-csv)
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("rows_ok", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("rows_bad", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )

    # PROCESSED_ROWS (con campos que tu backend ya referencia)
    op.create_table(
        "processed_rows",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("item", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("date_str", sa.String(length=50), nullable=True),
        sa.Column("line_hash", sa.String(length=64), nullable=True),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("user_id", sa.Integer(), nullable=True),

        sa.Column("nlp_overall_confidence", sa.Float(), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("review_status", sa.String(length=20), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),

        # Si tu pipeline relaciona filas con jobs, lo dejamos:
        sa.Column("job_id", sa.String(length=64), nullable=True),
    )

    op.create_index("ix_processed_rows_id", "processed_rows", ["id"], unique=False)
    op.create_index("ix_processed_rows_item", "processed_rows", ["item"], unique=False)
    op.create_index("ix_processed_rows_line_hash", "processed_rows", ["line_hash"], unique=False)

    # NLP_EXTRACTIONS (mínimo viable para que /nlp/extractions no reviente)
    op.create_table(
        "nlp_extractions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),

        sa.Column("item", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("date_str", sa.String(length=50), nullable=True),

        sa.Column("item_conf", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("amount_conf", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("date_conf", sa.Float(), nullable=False, server_default=sa.text("0")),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),

        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS nlp_extractions CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS processed_rows CASCADE;"))
    op.execute(sa.text("DROP TABLE IF EXISTS jobs CASCADE;"))
