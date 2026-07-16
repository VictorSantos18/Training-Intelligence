import sqlalchemy as sa
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE','PAUSED','ACHIEVED')", name="skills_status_check"),
        UniqueConstraint("user_id", "name", name="skills_user_name_unique"),
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
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=sa.text("'ACTIVE'"),
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

    user = relationship("Profile", back_populates="skills")
    exercises = relationship("Exercise", back_populates="skill")
    training_sessions = relationship("TrainingSession", back_populates="skill")
