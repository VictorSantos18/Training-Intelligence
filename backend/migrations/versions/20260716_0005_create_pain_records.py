"""create pain records

Revision ID: 20260716_0005
Revises: 20260716_0004
Create Date: 2026-07-16 15:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0005"
down_revision: str | None = "20260716_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pain_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("training_session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("training_set_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("body_region", sa.String(length=80), nullable=False),
        sa.Column("side", sa.String(length=20), nullable=False),
        sa.Column("moment", sa.String(length=20), nullable=False),
        sa.Column("intensity", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "moment IN ('PRE_SESSION','DURING_SET','POST_SESSION','CHECKIN_24H','CHECKIN_48H')",
            name="pain_records_moment_check",
        ),
        sa.CheckConstraint(
            "side IN ('LEFT','RIGHT','BILATERAL','NOT_APPLICABLE')",
            name="pain_records_side_check",
        ),
        sa.CheckConstraint(
            "intensity BETWEEN 0 AND 10",
            name="pain_records_intensity_check",
        ),
        sa.CheckConstraint(
            "training_session_id IS NOT NULL OR training_set_id IS NOT NULL",
            name="pain_records_training_context_required_check",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["training_session_id"],
            ["training_sessions.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["training_set_id"], ["training_sets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_pain_records_user_occurred", "pain_records", ["user_id", "occurred_at"])
    op.create_index(
        "idx_pain_records_session",
        "pain_records",
        ["training_session_id", "occurred_at"],
    )
    op.create_index("idx_pain_records_set", "pain_records", ["training_set_id"])


def downgrade() -> None:
    op.drop_index("idx_pain_records_set", table_name="pain_records")
    op.drop_index("idx_pain_records_session", table_name="pain_records")
    op.drop_index("idx_pain_records_user_occurred", table_name="pain_records")
    op.drop_table("pain_records")
