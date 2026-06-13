"""Migration: alert deliveries and tenant Slack webhooks."""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_alerts"
down_revision: Union[str, None] = "004_ops"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("slack_webhook_url", sa.Text(), nullable=True))

    op.create_table(
        "alert_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("change_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("alert_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["brief_id"], ["briefs.id"]),
        sa.ForeignKeyConstraint(["change_event_id"], ["change_events.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_alert_deliveries_brief_channel",
        "alert_deliveries",
        ["brief_id", "channel", "alert_type"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_alert_deliveries_brief_channel", table_name="alert_deliveries")
    op.drop_table("alert_deliveries")
    op.drop_column("tenants", "slack_webhook_url")
