from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_exercise import SessionExercise
from app.modules.exercises.repository import ExerciseRepository
from app.modules.session_exercises.exceptions import (
    SessionExerciseExerciseNotFoundError,
    SessionExerciseNotFoundError,
    SessionExerciseOrderAlreadyExistsError,
    SessionExerciseSkillMismatchError,
    SessionExerciseTrainingSessionClosedError,
    SessionExerciseTrainingSessionNotFoundError,
)
from app.modules.session_exercises.repository import SessionExerciseRepository
from app.modules.session_exercises.schemas import SessionExerciseCreate, SessionExerciseUpdate
from app.modules.sessions.repository import TrainingSessionRepository
from app.modules.sessions.schemas import TrainingSessionStatus


class SessionExerciseService:
    def __init__(
        self,
        session_exercise_repository: SessionExerciseRepository | None = None,
        training_session_repository: TrainingSessionRepository | None = None,
        exercise_repository: ExerciseRepository | None = None,
    ) -> None:
        self.session_exercise_repository = (
            session_exercise_repository or SessionExerciseRepository()
        )
        self.training_session_repository = (
            training_session_repository or TrainingSessionRepository()
        )
        self.exercise_repository = exercise_repository or ExerciseRepository()

    async def list_session_exercises(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
    ) -> list[SessionExercise]:
        training_session = await self.training_session_repository.get_by_id_and_user(
            session,
            training_session_id,
            user_id,
        )
        if training_session is None:
            raise SessionExerciseTrainingSessionNotFoundError

        return await self.session_exercise_repository.list_by_training_session(
            session,
            training_session_id,
        )

    async def create_session_exercise(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
        data: SessionExerciseCreate,
    ) -> SessionExercise:
        training_session = await self.training_session_repository.get_by_id_and_user(
            session,
            training_session_id,
            user_id,
        )
        if training_session is None:
            raise SessionExerciseTrainingSessionNotFoundError
        self._ensure_training_session_open(training_session.status)

        exercise = await self.exercise_repository.get_by_id_and_user(
            session,
            data.exercise_id,
            user_id,
        )
        if exercise is None:
            raise SessionExerciseExerciseNotFoundError
        self._ensure_exercise_matches_training_session_skill(
            exercise.skill_id,
            training_session.skill_id,
        )

        try:
            session_exercise = await self.session_exercise_repository.create(
                session,
                training_session_id,
                data,
            )
            await session.commit()
            await session.refresh(session_exercise)
            return session_exercise
        except IntegrityError as exc:
            await session.rollback()
            raise SessionExerciseOrderAlreadyExistsError from exc

    async def update_session_exercise(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
        data: SessionExerciseUpdate,
    ) -> SessionExercise:
        session_exercise = await self._get_session_exercise_for_open_training_session(
            session,
            session_exercise_id,
            user_id,
        )
        try:
            session_exercise = await self.session_exercise_repository.update(
                session,
                session_exercise,
                data,
            )
            await session.commit()
            await session.refresh(session_exercise)
            return session_exercise
        except IntegrityError as exc:
            await session.rollback()
            raise SessionExerciseOrderAlreadyExistsError from exc

    async def delete_session_exercise(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
    ) -> None:
        session_exercise = await self._get_session_exercise_for_open_training_session(
            session,
            session_exercise_id,
            user_id,
        )
        await self.session_exercise_repository.delete(session, session_exercise)
        await session.commit()

    async def _get_session_exercise_for_open_training_session(
        self,
        session: AsyncSession,
        session_exercise_id: UUID,
        user_id: str,
    ) -> SessionExercise:
        session_exercise = await self.session_exercise_repository.get_by_id_and_user(
            session,
            session_exercise_id,
            user_id,
        )
        if session_exercise is None:
            raise SessionExerciseNotFoundError
        await session.refresh(session_exercise, attribute_names=["training_session"])
        self._ensure_training_session_open(session_exercise.training_session.status)
        return session_exercise

    def _ensure_training_session_open(self, status: str) -> None:
        if status != TrainingSessionStatus.in_progress.value:
            raise SessionExerciseTrainingSessionClosedError

    def _ensure_exercise_matches_training_session_skill(
        self,
        exercise_skill_id: str | None,
        training_session_skill_id: str | None,
    ) -> None:
        if exercise_skill_id != training_session_skill_id:
            raise SessionExerciseSkillMismatchError
