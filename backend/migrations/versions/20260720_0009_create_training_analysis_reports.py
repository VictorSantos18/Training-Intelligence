"""create training analysis reports

Revision ID: 20260720_0009
Revises: 20260720_0008
Create Date: 2026-07-20 10:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0009"
down_revision: str | None = "20260720_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "training_analysis_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("skill_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generated_prompt", sa.Text(), nullable=False),
        sa.Column("external_analysis", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'PROMPT_GENERATED'"),
            nullable=False,
        ),
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
        sa.CheckConstraint(
            "period_end >= period_start",
            name="training_analysis_reports_period_check",
        ),
        sa.CheckConstraint(
            "status IN ('PROMPT_GENERATED','ANALYSIS_SAVED')",
            name="training_analysis_reports_status_check",
        ),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_analysis_reports_user_created",
        "training_analysis_reports",
        ["user_id", "created_at"],
    )
    op.create_index(
        "idx_analysis_reports_user_period",
        "training_analysis_reports",
        ["user_id", "period_start", "period_end"],
    )
    op.create_index(
        "idx_analysis_reports_user_skill",
        "training_analysis_reports",
        ["user_id", "skill_id"],
    )

    op.create_table(
        "training_analysis_report_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("analysis_report_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("training_session_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["analysis_report_id"],
            ["training_analysis_reports.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "analysis_report_id",
            "training_session_id",
            name="analysis_report_sessions_report_session_unique",
        ),
    )
    op.create_index(
        "idx_analysis_report_sessions_report",
        "training_analysis_report_sessions",
        ["analysis_report_id"],
    )
    op.create_index(
        "idx_analysis_report_sessions_session",
        "training_analysis_report_sessions",
        ["training_session_id"],
    )

    op.execute("ALTER TABLE public.training_analysis_reports ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.training_analysis_report_sessions ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.execute("ALTER TABLE public.training_analysis_report_sessions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.training_analysis_reports DISABLE ROW LEVEL SECURITY")
    op.drop_index(
        "idx_analysis_report_sessions_session",
        table_name="training_analysis_report_sessions",
    )
    op.drop_index(
        "idx_analysis_report_sessions_report",
        table_name="training_analysis_report_sessions",
    )
    op.drop_table("training_analysis_report_sessions")
    op.drop_index("idx_analysis_reports_user_skill", table_name="training_analysis_reports")
    op.drop_index("idx_analysis_reports_user_period", table_name="training_analysis_reports")
    op.drop_index("idx_analysis_reports_user_created", table_name="training_analysis_reports")
    op.drop_table("training_analysis_reports")
