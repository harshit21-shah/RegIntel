"""Migration: operational tables for ingestion and eval tracking."""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_ops"
down_revision: Union[str, None] = "003_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("document_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_runs_source_started", "ingestion_runs", ["source", "started_at"])

    op.create_table(
        "eval_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("suite", sa.Text(), nullable=False),
        sa.Column("cases", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Numeric(5, 4), nullable=False),
        sa.Column("threshold", sa.Numeric(5, 4), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("eval_runs")
    op.drop_index("ix_ingestion_runs_source_started", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
