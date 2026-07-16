import sqlalchemy as sa
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=sa.text("'America/Sao_Paulo'"),
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

    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="user", cascade="all, delete-orphan")
    training_sessions = relationship(
        "TrainingSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
