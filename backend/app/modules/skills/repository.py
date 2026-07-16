from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.modules.skills.schemas import SkillCreate, SkillUpdate


class SkillRepository:
    async def list_by_user(self, session: AsyncSession, user_id: str) -> list[Skill]:
        result = await session.execute(
            select(Skill).where(Skill.user_id == user_id).order_by(Skill.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        skill_id: UUID,
        user_id: str,
    ) -> Skill | None:
        result = await session.execute(
            select(Skill).where(Skill.id == str(skill_id), Skill.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, user_id: str, data: SkillCreate) -> Skill:
        skill = Skill(
            user_id=user_id,
            name=data.name,
            description=data.description,
            status=data.status.value,
        )
        session.add(skill)
        await session.flush()
        return skill

    async def update(self, session: AsyncSession, skill: Skill, data: SkillUpdate) -> Skill:
        values = data.model_dump(exclude_unset=True)
        if "status" in values and values["status"] is not None:
            values["status"] = values["status"].value

        for field, value in values.items():
            setattr(skill, field, value)

        await session.flush()
        return skill

    async def delete(self, session: AsyncSession, skill: Skill) -> None:
        await session.delete(skill)
        await session.flush()

