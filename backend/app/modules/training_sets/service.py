from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training_set import TrainingSet
from app.modules.session_exercises.repository import SessionExerciseRepository
from app.modules.sessions.schemas import TrainingSessionStatus
from app.modules.training_sets.exceptions import (
    TrainingSetNotFoundError,
    TrainingSetNumberAlreadyExistsError,
    TrainingSetSessionClosedError,
    TrainingSetSessionExerciseNotFoundError,
)
from app.modules.training_sets.repository import TrainingSetRepository
from app.modules.training_sets.schemas import (
    TrainingSetCreate,
    TrainingSetResult,
    TrainingSetUpdate,
)


class TrainingSetService:
    def __init__(
        self,
        training_set_repository: TrainingSetRepository | None = None,
        session_exercise_repository: SessionExerciseRepository | None = None,
    ) -> None:
        self.training_set_repository = training_set_repository or TrainingSetRepository()
        self.session_exercise_repository = (
            session_exercise_repository or SessionExerciseRepository()
        )

    async def list_training_sets(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
    ) -> list[TrainingSet]:
        session_exercise = await self.session_exercise_repository.get_by_id_and_user(
            session,
            session_exercise_id,
            user_id,
        )
        if session_exercise is None:
            raise TrainingSetSessionExerciseNotFoundError

        return await self.training_set_repository.list_by_session_exercise(
            session,
            session_exercise_id,
        )

    async def create_training_set(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
        data: TrainingSetCreate,
    ) -> TrainingSet:
        session_exercise = await self.session_exercise_repository.get_by_id_and_user(
            session,
            session_exercise_id,
            user_id,
        )
        if session_exercise is None:
            raise TrainingSetSessionExerciseNotFoundError
        await session.refresh(session_exercise, attribute_names=["training_session"])
        self._ensure_training_session_open(session_exercise.training_session.status)

        try:
            training_set = await self.training_set_repository.create(
                session,
                session_exercise_id,
                data,
            )
            await session.commit()
            await session.refresh(training_set)
            return training_set
        except IntegrityError as exc:
            await session.rollback()
            raise TrainingSetNumberAlreadyExistsError from exc

    async def update_training_set(
        self,
        session: AsyncSession,
        training_set_id: UUID,
        user_id: str,
        data: TrainingSetUpdate,
    ) -> TrainingSet:
        training_set = await self._get_training_set_for_open_training_session(
            session,
            training_set_id,
            user_id,
        )
        self._validate_update_metrics(training_set, data)
        try:
            training_set = await self.training_set_repository.update(session, training_set, data)
            await session.commit()
            await session.refresh(training_set)
            return training_set
        except IntegrityError as exc:
            await session.rollback()
            raise TrainingSetNumberAlreadyExistsError from exc

    async def delete_training_set(
        self,
        session: AsyncSession,
        training_set_id: UUID,
        user_id: str,
    ) -> None:
        training_set = await self._get_training_set_for_open_training_session(
            session,
            training_set_id,
            user_id,
        )
        await self.training_set_repository.delete(session, training_set)
        await session.commit()

    async def _get_training_set_for_open_training_session(
        self,
        session: AsyncSession,
        training_set_id: UUID,
        user_id: str,
    ) -> TrainingSet:
        training_set = await self.training_set_repository.get_by_id_and_user(
            session,
            training_set_id,
            user_id,
        )
        if training_set is None:
            raise TrainingSetNotFoundError
        await session.refresh(training_set, attribute_names=["session_exercise"])
        await session.refresh(training_set.session_exercise, attribute_names=["training_session"])
        self._ensure_training_session_open(training_set.session_exercise.training_session.status)
        return training_set

    def _ensure_training_session_open(self, status: str) -> None:
        if status != TrainingSessionStatus.in_progress.value:
            raise TrainingSetSessionClosedError

    def _validate_update_metrics(
        self,
        training_set: TrainingSet,
        data: TrainingSetUpdate,
    ) -> None:
        result = data.result.value if data.result else training_set.result
        repetitions = (
            data.repetitions
            if "repetitions" in data.model_fields_set
            else training_set.repetitions
        )
        duration_seconds = (
            data.duration_seconds
            if "duration_seconds" in data.model_fields_set
            else training_set.duration_seconds
        )
        if (
            result != TrainingSetResult.skipped.value
            and repetitions is None
            and duration_seconds is None
        ):
            raise ValueError("Non-skipped sets require repetitions or duration_seconds")
