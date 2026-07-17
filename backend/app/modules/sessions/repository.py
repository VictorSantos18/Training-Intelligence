from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training_session import TrainingSession
from app.modules.sessions.schemas import (
    TrainingSessionCreate,
    TrainingSessionFinish,
    TrainingSessionStatus,
    TrainingSessionUpdate,
)


class TrainingSessionRepository:
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: str,
        skill_id: UUID | None = None,
        status: TrainingSessionStatus | None = None,
    ) -> list[TrainingSession]:
        query = select(TrainingSession).where(TrainingSession.user_id == user_id)
        if skill_id is not None:
            query = query.where(TrainingSession.skill_id == str(skill_id))
        if status is not None:
            query = query.where(TrainingSession.status == status.value)

        result = await session.execute(query.order_by(TrainingSession.started_at.desc()))
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
    ) -> TrainingSession | None:
        result = await session.execute(
            select(TrainingSession).where(
                TrainingSession.id == str(training_session_id),
                TrainingSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        user_id: str,
        data: TrainingSessionCreate,
    ) -> TrainingSession:
        training_session = TrainingSession(
            user_id=user_id,
            skill_id=str(data.skill_id) if data.skill_id is not None else None,
            started_at=data.started_at,
            sleep_hours=data.sleep_hours,
            energy_before=data.energy_before,
        )
        session.add(training_session)
        await session.flush()
        return training_session

    async def update(
        self,
        session: AsyncSession,
        training_session: TrainingSession,
        data: TrainingSessionUpdate,
    ) -> TrainingSession:
        values = data.model_dump(exclude_unset=True)
        if "skill_id" in values and values["skill_id"] is not None:
            values["skill_id"] = str(values["skill_id"])

        for field, value in values.items():
            setattr(training_session, field, value)

        await session.flush()
        return training_session

    async def finish(
        self,
        session: AsyncSession,
        training_session: TrainingSession,
        data: TrainingSessionFinish,
    ) -> TrainingSession:
        values = data.model_dump(exclude_unset=True)
        for field, value in values.items():
            setattr(training_session, field, value)
        training_session.status = TrainingSessionStatus.completed.value
        await session.flush()
        return training_session

    async def cancel(
        self,
        session: AsyncSession,
        training_session: TrainingSession,
    ) -> TrainingSession:
        training_session.status = TrainingSessionStatus.cancelled.value
        await session.flush()
        return training_session
