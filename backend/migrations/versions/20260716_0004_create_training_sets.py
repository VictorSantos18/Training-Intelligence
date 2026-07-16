"""create training sets

Revision ID: 20260716_0004
Revises: 20260716_0003
Create Date: 2026-07-16 14:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0004"
down_revision: str | None = "20260716_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "training_sets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_exercise_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("set_number", sa.SmallInteger(), nullable=False),
        sa.Column("repetitions", sa.SmallInteger(), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(6, 2), nullable=True),
        sa.Column("assistance_level", sa.Numeric(8, 2), nullable=True),
        sa.Column("rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("pain_during", sa.SmallInteger(), nullable=True),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("technical_quality", sa.String(length=20), nullable=True),
        sa.Column("rest_seconds", sa.SmallInteger(), nullable=True),
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
            "result IN ('SUCCESS','PARTIAL','FAILED','SKIPPED')",
            name="training_sets_result_check",
        ),
        sa.CheckConstraint(
            "technical_quality IS NULL OR technical_quality IN "
            "('EXCELLENT','GOOD','ACCEPTABLE','POOR')",
            name="training_sets_technical_quality_check",
        ),
        sa.CheckConstraint(
            "rpe IS NULL OR rpe BETWEEN 0 AND 10",
            name="training_sets_rpe_check",
        ),
        sa.CheckConstraint(
            "pain_during IS NULL OR pain_during BETWEEN 0 AND 10",
            name="training_sets_pain_during_check",
        ),
        sa.CheckConstraint(
            "result = 'SKIPPED' OR repetitions IS NOT NULL OR duration_seconds IS NOT NULL",
            name="training_sets_metric_required_check",
        ),
        sa.ForeignKeyConstraint(
            ["session_exercise_id"],
            ["session_exercises.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_exercise_id",
            "set_number",
            name="training_sets_session_exercise_set_number_unique",
        ),
    )
    op.create_index(
        "idx_training_sets_session_exercise",
        "training_sets",
        ["session_exercise_id", "set_number"],
    )


def downgrade() -> None:
    op.drop_index("idx_training_sets_session_exercise", table_name="training_sets")
    op.drop_table("training_sets")
