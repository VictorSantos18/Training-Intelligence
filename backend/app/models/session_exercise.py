import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SessionExercise(Base):
    __tablename__ = "session_exercises"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "execution_order",
            name="session_exercises_session_order_unique",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
    )
    execution_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    training_session = relationship("TrainingSession", back_populates="session_exercises")
    exercise = relationship("Exercise", back_populates="session_exercises")
