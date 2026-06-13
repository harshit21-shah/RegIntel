"""Add relevance_weights table for feedback-driven scoring."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_relevance_weights"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relevance_weights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("edge_type", sa.Text(), nullable=False),
        sa.Column("hop_depth", sa.Integer(), nullable=False),
        sa.Column("naics_code", sa.Text(), nullable=True),
        sa.Column("weight", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("edge_type", "hop_depth", "naics_code", name="uq_relevance_weight_key"),
    )
    op.add_column(
        "feedback", sa.Column("hop_path", postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("feedback", "hop_path")
    op.drop_table("relevance_weights")
