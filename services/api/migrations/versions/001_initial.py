"""Initial Postgres schema v1."""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("plan", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "client_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("naics_codes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("states_of_operation", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("product_categories", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("supply_chain_jurisdictions", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", sa.Text(), nullable=False),
        sa.Column("clause_id", sa.Text(), nullable=False),
        sa.Column("change_type", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("old_text", sa.Text(), nullable=True),
        sa.Column("new_text", sa.Text(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("change_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("obligations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recommended_actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["change_event_id"], ["change_events.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["client_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "brief_citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("clause_id", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["brief_id"], ["briefs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["brief_id"], ["briefs.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "agent_traces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("change_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.Text(), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("model_used", sa.Text(), nullable=False),
        sa.Column("prompt_version", sa.Text(), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["brief_id"], ["briefs.id"]),
        sa.ForeignKeyConstraint(["change_event_id"], ["change_events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "llm_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["trace_id"], ["agent_traces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("llm_usage")
    op.drop_table("agent_traces")
    op.drop_table("feedback")
    op.drop_table("brief_citations")
    op.drop_table("briefs")
    op.drop_table("change_events")
    op.drop_table("client_profiles")
    op.drop_table("users")
    op.drop_table("tenants")
