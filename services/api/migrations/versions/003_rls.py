"""Row-level security policies for tenant isolation."""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "003_rls"
down_revision: Union[str, None] = "002_relevance_weights"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TENANT_TABLES = ("client_profiles", "briefs", "feedback")


def upgrade() -> None:
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY client_profiles_tenant_isolation ON client_profiles
        USING (
            tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
        )
        WITH CHECK (
            tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
        )
        """)
    op.execute("""
        CREATE POLICY briefs_tenant_isolation ON briefs
        USING (
            client_id IN (
                SELECT id FROM client_profiles
                WHERE tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
            )
        )
        """)
    op.execute("""
        CREATE POLICY feedback_tenant_isolation ON feedback
        USING (
            brief_id IN (
                SELECT b.id FROM briefs b
                JOIN client_profiles cp ON cp.id = b.client_id
                WHERE cp.tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
            )
        )
        """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS feedback_tenant_isolation ON feedback")
    op.execute("DROP POLICY IF EXISTS briefs_tenant_isolation ON briefs")
    op.execute("DROP POLICY IF EXISTS client_profiles_tenant_isolation ON client_profiles")
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
