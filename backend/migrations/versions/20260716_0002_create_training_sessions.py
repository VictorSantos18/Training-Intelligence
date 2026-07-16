"""create training sessions

Revision ID: 20260716_0002
Revises: 20260716_0001
Create Date: 2026-07-16 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0002"
down_revision: str | None = "20260716_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "training_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("body_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("sleep_hours", sa.Numeric(4, 2), nullable=True),
        sa.Column("sleep_quality", sa.SmallInteger(), nullable=True),
        sa.Column("energy_before", sa.SmallInteger(), nullable=True),
        sa.Column("motivation_before", sa.SmallInteger(), nullable=True),
        sa.Column("fatigue_before", sa.SmallInteger(), nullable=True),
        sa.Column("fatigue_after", sa.SmallInteger(), nullable=True),
        sa.Column("performance_rating", sa.SmallInteger(), nullable=True),
        sa.Column("notes_before", sa.Text(), nullable=True),
        sa.Column("notes_after", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'IN_PROGRESS'"),
            nullable=False,
        ),
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
            "status IN ('IN_PROGRESS','COMPLETED','CANCELLED')",
            name="training_sessions_status_check",
        ),
        sa.CheckConstraint(
            "sleep_quality IS NULL OR sleep_quality BETWEEN 0 AND 10",
            name="training_sessions_sleep_quality_check",
        ),
        sa.CheckConstraint(
            "energy_before IS NULL OR energy_before BETWEEN 0 AND 10",
            name="training_sessions_energy_before_check",
        ),
        sa.CheckConstraint(
            "motivation_before IS NULL OR motivation_before BETWEEN 0 AND 10",
            name="training_sessions_motivation_before_check",
        ),
        sa.CheckConstraint(
            "fatigue_before IS NULL OR fatigue_before BETWEEN 0 AND 10",
            name="training_sessions_fatigue_before_check",
        ),
        sa.CheckConstraint(
            "fatigue_after IS NULL OR fatigue_after BETWEEN 0 AND 10",
            name="training_sessions_fatigue_after_check",
        ),
        sa.CheckConstraint(
            "performance_rating IS NULL OR performance_rating BETWEEN 0 AND 10",
            name="training_sessions_performance_rating_check",
        ),
        sa.CheckConstraint(
            "finished_at IS NULL OR finished_at > started_at",
            name="training_sessions_finished_after_started_check",
        ),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_sessions_user_started",
        "training_sessions",
        ["user_id", "started_at"],
    )
    op.create_index(
        "idx_sessions_user_skill_started",
        "training_sessions",
        ["user_id", "skill_id", "started_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_sessions_user_skill_started", table_name="training_sessions")
    op.drop_index("idx_sessions_user_started", table_name="training_sessions")
    op.drop_table("training_sessions")
