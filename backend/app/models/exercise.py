import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint(
            "category IN ('HOLD','PRESS','PULL','RAISE','NEGATIVE','ACCESSORY')",
            name="exercises_category_check",
        ),
        CheckConstraint(
            "measurement_type IN ('REPS','SECONDS','DISTANCE','CUSTOM')",
            name="exercises_measurement_type_check",
        ),
        UniqueConstraint("user_id", "name", name="exercises_user_name_unique"),
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
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    measurement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=sa.text("true"),
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

    user = relationship("Profile", back_populates="exercises")
    skill = relationship("Skill", back_populates="exercises")
    session_exercises = relationship("SessionExercise", back_populates="exercise")
