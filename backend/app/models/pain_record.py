import sqlalchemy as sa
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PainRecord(Base):
    __tablename__ = "pain_records"
    __table_args__ = (
        CheckConstraint(
            "moment IN ('PRE_SESSION','DURING_SET','POST_SESSION','CHECKIN_24H','CHECKIN_48H')",
            name="pain_records_moment_check",
        ),
        CheckConstraint(
            "side IN ('LEFT','RIGHT','BILATERAL','NOT_APPLICABLE')",
            name="pain_records_side_check",
        ),
        CheckConstraint(
            "intensity BETWEEN 0 AND 10",
            name="pain_records_intensity_check",
        ),
        CheckConstraint(
            "training_session_id IS NOT NULL OR training_set_id IS NOT NULL",
            name="pain_records_training_context_required_check",
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
    training_session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("training_sessions.id", ondelete="SET NULL"),
    )
    training_set_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("training_sets.id", ondelete="SET NULL"),
    )
    occurred_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    body_region: Mapped[str] = mapped_column(String(80), nullable=False)
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    moment: Mapped[str] = mapped_column(String(20), nullable=False)
    intensity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
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

    user = relationship("Profile", back_populates="pain_records")
    training_session = relationship("TrainingSession", back_populates="pain_records")
    training_set = relationship("TrainingSet", back_populates="pain_records")
