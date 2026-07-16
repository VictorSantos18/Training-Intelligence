import sqlalchemy as sa
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrainingSet(Base):
    __tablename__ = "training_sets"
    __table_args__ = (
        CheckConstraint(
            "result IN ('SUCCESS','PARTIAL','FAILED','SKIPPED')",
            name="training_sets_result_check",
        ),
        CheckConstraint(
            "technical_quality IS NULL OR technical_quality IN "
            "('EXCELLENT','GOOD','ACCEPTABLE','POOR')",
            name="training_sets_technical_quality_check",
        ),
        CheckConstraint(
            "rpe IS NULL OR rpe BETWEEN 0 AND 10",
            name="training_sets_rpe_check",
        ),
        CheckConstraint(
            "pain_during IS NULL OR pain_during BETWEEN 0 AND 10",
            name="training_sets_pain_during_check",
        ),
        CheckConstraint(
            "result = 'SKIPPED' OR repetitions IS NOT NULL OR duration_seconds IS NOT NULL",
            name="training_sets_metric_required_check",
        ),
        UniqueConstraint(
            "session_exercise_id",
            "set_number",
            name="training_sets_session_exercise_set_number_unique",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    session_exercise_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("session_exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    set_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    repetitions: Mapped[int | None] = mapped_column(SmallInteger)
    duration_seconds: Mapped[Numeric | None] = mapped_column(Numeric(6, 2))
    assistance_level: Mapped[Numeric | None] = mapped_column(Numeric(8, 2))
    rpe: Mapped[Numeric | None] = mapped_column(Numeric(3, 1))
    pain_during: Mapped[int | None] = mapped_column(SmallInteger)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    technical_quality: Mapped[str | None] = mapped_column(String(20))
    rest_seconds: Mapped[int | None] = mapped_column(SmallInteger)
    notes: Mapped[str | None] = mapped_column(Text)
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

    session_exercise = relationship("SessionExercise", back_populates="training_sets")
