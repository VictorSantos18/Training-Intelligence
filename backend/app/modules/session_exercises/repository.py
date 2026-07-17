from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_exercise import SessionExercise
from app.models.training_session import TrainingSession
from app.modules.session_exercises.schemas import SessionExerciseCreate, SessionExerciseUpdate


class SessionExerciseRepository:
    async def list_by_training_session(
        self,
        session: AsyncSession,
        training_session_id: UUID,
    ) -> list[SessionExercise]:
        result = await session.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == str(training_session_id))
            .order_by(SessionExercise.execution_order.asc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
    ) -> SessionExercise | None:
        result = await session.execute(
            select(SessionExercise)
            .join(TrainingSession, SessionExercise.session_id == TrainingSession.id)
            .where(
                SessionExercise.id == str(session_exercise_id),
                TrainingSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        data: SessionExerciseCreate,
    ) -> SessionExercise:
        session_exercise = SessionExercise(
            session_id=str(training_session_id),
            exercise_id=str(data.exercise_id),
            execution_order=data.execution_order,
            notes=data.notes,
        )
        session.add(session_exercise)
        await session.flush()
        return session_exercise

    async def update(
        self,
        session: AsyncSession,
        session_exercise: SessionExercise,
        data: SessionExerciseUpdate,
    ) -> SessionExercise:
        values = data.model_dump(exclude_unset=True)
        for field, value in values.items():
            setattr(session_exercise, field, value)

        await session.flush()
        return session_exercise

    async def delete(self, session: AsyncSession, session_exercise: SessionExercise) -> None:
        await session.delete(session_exercise)
        await session.flush()
