"""enable rls on public tables

Revision ID: 20260720_0008
Revises: 20260717_0007
Create Date: 2026-07-20 09:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260720_0008"
down_revision: str | None = "20260717_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PUBLIC_TABLES_WITH_RLS = (
    "alembic_version",
    "profiles",
    "skills",
    "exercises",
    "training_sessions",
    "session_exercises",
    "training_sets",
    "pain_records",
    "body_regions",
)


def upgrade() -> None:
    for table_name in PUBLIC_TABLES_WITH_RLS:
        op.execute(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table_name in reversed(PUBLIC_TABLES_WITH_RLS):
        op.execute(f"ALTER TABLE public.{table_name} DISABLE ROW LEVEL SECURITY")
