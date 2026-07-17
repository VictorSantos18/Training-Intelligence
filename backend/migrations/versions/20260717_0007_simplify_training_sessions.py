"""simplify training sessions

Revision ID: 20260717_0007
Revises: 20260717_0006
Create Date: 2026-07-17 10:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260717_0007"
down_revision: str | None = "20260717_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


REMOVED_CHECK_CONSTRAINTS = [
    "training_sessions_sleep_quality_check",
    "training_sessions_motivation_before_check",
    "training_sessions_fatigue_before_check",
    "training_sessions_fatigue_after_check",
    "training_sessions_performance_rating_check",
]

REMOVED_COLUMNS = [
    "body_weight_kg",
    "sleep_quality",
    "motivation_before",
    "fatigue_before",
    "fatigue_after",
    "performance_rating",
    "notes_before",
]


def upgrade() -> None:
    for constraint_name in REMOVED_CHECK_CONSTRAINTS:
        op.drop_constraint(constraint_name, "training_sessions", type_="check")

    for column_name in REMOVED_COLUMNS:
        op.drop_column("training_sessions", column_name)


def downgrade() -> None:
    op.add_column(
        "training_sessions",
        sa.Column("body_weight_kg", sa.Numeric(5, 2), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("sleep_quality", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("motivation_before", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("fatigue_before", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("fatigue_after", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("performance_rating", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "training_sessions",
        sa.Column("notes_before", sa.Text(), nullable=True),
    )

    op.create_check_constraint(
        "training_sessions_sleep_quality_check",
        "training_sessions",
        "sleep_quality IS NULL OR sleep_quality BETWEEN 0 AND 10",
    )
    op.create_check_constraint(
        "training_sessions_motivation_before_check",
        "training_sessions",
        "motivation_before IS NULL OR motivation_before BETWEEN 0 AND 10",
    )
    op.create_check_constraint(
        "training_sessions_fatigue_before_check",
        "training_sessions",
        "fatigue_before IS NULL OR fatigue_before BETWEEN 0 AND 10",
    )
    op.create_check_constraint(
        "training_sessions_fatigue_after_check",
        "training_sessions",
        "fatigue_after IS NULL OR fatigue_after BETWEEN 0 AND 10",
    )
    op.create_check_constraint(
        "training_sessions_performance_rating_check",
        "training_sessions",
        "performance_rating IS NULL OR performance_rating BETWEEN 0 AND 10",
    )
