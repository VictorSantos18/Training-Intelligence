from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_exercise import SessionExercise
from app.models.training_session import TrainingSession
from app.models.training_set import TrainingSet
from app.modules.training_sets.schemas import TrainingSetCreate, TrainingSetUpdate


class TrainingSetRepository:
    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        training_set_id: UUID,
        user_id: str,
    ) -> TrainingSet | None:
        result = await session.execute(
            select(TrainingSet)
            .join(SessionExercise, TrainingSet.session_exercise_id == SessionExercise.id)
            .join(TrainingSession, SessionExercise.session_id == TrainingSession.id)
            .where(
                TrainingSet.id == str(training_set_id),
                TrainingSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        data: TrainingSetCreate,
    ) -> TrainingSet:
        training_set = TrainingSet(
            session_exercise_id=str(session_exercise_id),
            set_number=data.set_number,
            repetitions=data.repetitions,
            duration_seconds=data.duration_seconds,
            assistance_level=data.assistance_level,
            rpe=data.rpe,
            pain_during=data.pain_during,
            result=data.result.value,
            technical_quality=data.technical_quality.value if data.technical_quality else None,
            rest_seconds=data.rest_seconds,
            notes=data.notes,
        )
        session.add(training_set)
        await session.flush()
        return training_set

    async def update(
        self,
        session: AsyncSession,
        training_set: TrainingSet,
        data: TrainingSetUpdate,
    ) -> TrainingSet:
        values = data.model_dump(exclude_unset=True)
        for field in ("result", "technical_quality"):
            if field in values and values[field] is not None:
                values[field] = values[field].value

        for field, value in values.items():
            setattr(training_set, field, value)

        await session.flush()
        return training_set

    async def delete(self, session: AsyncSession, training_set: TrainingSet) -> None:
        await session.delete(training_set)
        await session.flush()

