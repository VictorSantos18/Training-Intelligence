import sqlalchemy as sa
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrainingSession(Base):
    __tablename__ = "training_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('IN_PROGRESS','COMPLETED','CANCELLED')",
            name="training_sessions_status_check",
        ),
        CheckConstraint(
            "sleep_quality IS NULL OR sleep_quality BETWEEN 0 AND 10",
            name="training_sessions_sleep_quality_check",
        ),
        CheckConstraint(
            "energy_before IS NULL OR energy_before BETWEEN 0 AND 10",
            name="training_sessions_energy_before_check",
        ),
        CheckConstraint(
            "motivation_before IS NULL OR motivation_before BETWEEN 0 AND 10",
            name="training_sessions_motivation_before_check",
        ),
        CheckConstraint(
            "fatigue_before IS NULL OR fatigue_before BETWEEN 0 AND 10",
            name="training_sessions_fatigue_before_check",
        ),
        CheckConstraint(
            "fatigue_after IS NULL OR fatigue_after BETWEEN 0 AND 10",
            name="training_sessions_fatigue_after_check",
        ),
        CheckConstraint(
            "performance_rating IS NULL OR performance_rating BETWEEN 0 AND 10",
            name="training_sessions_performance_rating_check",
        ),
        CheckConstraint(
            "finished_at IS NULL OR finished_at > started_at",
            name="training_sessions_finished_after_started_check",
        ),
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
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    body_weight_kg: Mapped[Numeric | None] = mapped_column(Numeric(5, 2))
    sleep_hours: Mapped[Numeric | None] = mapped_column(Numeric(4, 2))
    sleep_quality: Mapped[int | None] = mapped_column(SmallInteger)
    energy_before: Mapped[int | None] = mapped_column(SmallInteger)
    motivation_before: Mapped[int | None] = mapped_column(SmallInteger)
    fatigue_before: Mapped[int | None] = mapped_column(SmallInteger)
    fatigue_after: Mapped[int | None] = mapped_column(SmallInteger)
    performance_rating: Mapped[int | None] = mapped_column(SmallInteger)
    notes_before: Mapped[str | None] = mapped_column(Text)
    notes_after: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=sa.text("'IN_PROGRESS'"),
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

    user = relationship("Profile", back_populates="training_sessions")
    skill = relationship("Skill", back_populates="training_sessions")
    session_exercises = relationship(
        "SessionExercise",
        back_populates="training_session",
        cascade="all, delete-orphan",
    )
