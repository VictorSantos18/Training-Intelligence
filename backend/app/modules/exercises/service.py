from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.modules.exercises.exceptions import (
    ExerciseNameAlreadyExistsError,
    ExerciseNotFoundError,
    ExerciseSkillNotFoundError,
)
from app.modules.exercises.repository import ExerciseRepository
from app.modules.exercises.schemas import ExerciseCreate, ExerciseUpdate
from app.modules.profiles.repository import ProfileRepository
from app.modules.skills.repository import SkillRepository


class ExerciseService:
    def __init__(
        self,
        exercise_repository: ExerciseRepository | None = None,
        profile_repository: ProfileRepository | None = None,
        skill_repository: SkillRepository | None = None,
    ) -> None:
        self.exercise_repository = exercise_repository or ExerciseRepository()
        self.profile_repository = profile_repository or ProfileRepository()
        self.skill_repository = skill_repository or SkillRepository()

    async def list_exercises(
        self,
        session: AsyncSession,
        user_id: str,
        skill_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[Exercise]:
        return await self.exercise_repository.list_by_user(session, user_id, skill_id, is_active)

    async def get_exercise(
        self,
        session: AsyncSession,
        exercise_id: UUID,
        user_id: str,
    ) -> Exercise:
        exercise = await self.exercise_repository.get_by_id_and_user(
            session,
            exercise_id,
            user_id,
        )
        if exercise is None:
            raise ExerciseNotFoundError
        return exercise

    async def create_exercise(
        self,
        session: AsyncSession,
        user_id: str,
        data: ExerciseCreate,
    ) -> Exercise:
        try:
            await self.profile_repository.ensure_exists(session, user_id)
            await self._ensure_skill_belongs_to_user(session, data.skill_id, user_id)
            exercise = await self.exercise_repository.create(session, user_id, data)
            await session.commit()
            await session.refresh(exercise)
            return exercise
        except IntegrityError as exc:
            await session.rollback()
            raise ExerciseNameAlreadyExistsError from exc

    async def update_exercise(
        self,
        session: AsyncSession,
        exercise_id: UUID,
        user_id: str,
        data: ExerciseUpdate,
    ) -> Exercise:
        exercise = await self.get_exercise(session, exercise_id, user_id)
        try:
            if "skill_id" in data.model_fields_set:
                await self._ensure_skill_belongs_to_user(session, data.skill_id, user_id)
            exercise = await self.exercise_repository.update(session, exercise, data)
            await session.commit()
            await session.refresh(exercise)
            return exercise
        except IntegrityError as exc:
            await session.rollback()
            raise ExerciseNameAlreadyExistsError from exc

    async def deactivate_exercise(
        self,
        session: AsyncSession,
        exercise_id: UUID,
        user_id: str,
    ) -> Exercise:
        exercise = await self.get_exercise(session, exercise_id, user_id)
        exercise = await self.exercise_repository.deactivate(session, exercise)
        await session.commit()
        await session.refresh(exercise)
        return exercise

    async def _ensure_skill_belongs_to_user(
        self,
        session: AsyncSession,
        skill_id: UUID | None,
        user_id: str,
    ) -> None:
        if skill_id is None:
            return
        skill = await self.skill_repository.get_by_id_and_user(session, skill_id, user_id)
        if skill is None:
            raise ExerciseSkillNotFoundError

