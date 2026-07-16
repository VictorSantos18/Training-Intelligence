"""create session exercises

Revision ID: 20260716_0003
Revises: 20260716_0002
Create Date: 2026-07-16 13:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0003"
down_revision: str | None = "20260716_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "session_exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("execution_order", sa.SmallInteger(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["session_id"], ["training_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "execution_order",
            name="session_exercises_session_order_unique",
        ),
    )
    op.create_index(
        "idx_session_exercises_session",
        "session_exercises",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_session_exercises_session", table_name="session_exercises")
    op.drop_table("session_exercises")
