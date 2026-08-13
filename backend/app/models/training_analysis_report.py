import sqlalchemy as sa
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrainingAnalysisReport(Base):
    __tablename__ = "training_analysis_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PROMPT_GENERATED','ANALYSIS_SAVED')",
            name="training_analysis_reports_status_check",
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="training_analysis_reports_period_check",
        ),
        sa.Index("idx_analysis_reports_user_created", "user_id", "created_at"),
        sa.Index("idx_analysis_reports_user_period", "user_id", "period_start", "period_end"),
        sa.Index("idx_analysis_reports_user_skill", "user_id", "skill_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("skills.id", ondelete="SET NULL"),
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    period_end: Mapped[Date] = mapped_column(Date, nullable=False)
    filters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    summary_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    external_analysis: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=sa.text("'PROMPT_GENERATED'"),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("Profile", back_populates="analysis_reports")
    skill = relationship("Skill")
    sessions = relationship(
        "TrainingAnalysisReportSession",
        back_populates="analysis_report",
        cascade="all, delete-orphan",
    )


class TrainingAnalysisReportSession(Base):
    __tablename__ = "training_analysis_report_sessions"
    __table_args__ = (
        sa.UniqueConstraint(
            "analysis_report_id",
            "training_session_id",
            name="analysis_report_sessions_report_session_unique",
        ),
        sa.Index("idx_analysis_report_sessions_report", "analysis_report_id"),
        sa.Index("idx_analysis_report_sessions_session", "training_session_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    analysis_report_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("training_analysis_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    training_session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    analysis_report = relationship("TrainingAnalysisReport", back_populates="sessions")
