from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.modules.exercises.schemas import ExerciseCreate, ExerciseUpdate


class ExerciseRepository:
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: str,
        skill_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> list[Exercise]:
        query = select(Exercise).where(Exercise.user_id == user_id)
        if skill_id is not None:
            query = query.where(Exercise.skill_id == str(skill_id))
        if is_active is not None:
            query = query.where(Exercise.is_active == is_active)

        result = await session.execute(query.order_by(Exercise.name.asc()))
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        exercise_id: UUID,
        user_id: str,
    ) -> Exercise | None:
        result = await session.execute(
            select(Exercise).where(Exercise.id == str(exercise_id), Exercise.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, user_id: str, data: ExerciseCreate) -> Exercise:
        exercise = Exercise(
            user_id=user_id,
            skill_id=str(data.skill_id) if data.skill_id is not None else None,
            name=data.name,
            category=data.category.value,
            measurement_type=data.measurement_type.value,
        )
        session.add(exercise)
        await session.flush()
        return exercise

    async def update(
        self,
        session: AsyncSession,
        exercise: Exercise,
        data: ExerciseUpdate,
    ) -> Exercise:
        values = data.model_dump(exclude_unset=True)
        for field in ("category", "measurement_type"):
            if field in values and values[field] is not None:
                values[field] = values[field].value
        if "skill_id" in values and values["skill_id"] is not None:
            values["skill_id"] = str(values["skill_id"])

        for field, value in values.items():
            setattr(exercise, field, value)

        await session.flush()
        return exercise

    async def deactivate(self, session: AsyncSession, exercise: Exercise) -> Exercise:
        exercise.is_active = False
        await session.flush()
        return exercise

