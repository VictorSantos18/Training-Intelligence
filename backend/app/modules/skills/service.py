from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.modules.profiles.repository import ProfileRepository
from app.modules.skills.exceptions import SkillNameAlreadyExistsError, SkillNotFoundError
from app.modules.skills.repository import SkillRepository
from app.modules.skills.schemas import SkillCreate, SkillUpdate


class SkillService:
    def __init__(
        self,
        skill_repository: SkillRepository | None = None,
        profile_repository: ProfileRepository | None = None,
    ) -> None:
        self.skill_repository = skill_repository or SkillRepository()
        self.profile_repository = profile_repository or ProfileRepository()

    async def list_skills(self, session: AsyncSession, user_id: str) -> list[Skill]:
        return await self.skill_repository.list_by_user(session, user_id)

    async def get_skill(self, session: AsyncSession, skill_id: UUID, user_id: str) -> Skill:
        skill = await self.skill_repository.get_by_id_and_user(session, skill_id, user_id)
        if skill is None:
            raise SkillNotFoundError
        return skill

    async def create_skill(self, session: AsyncSession, user_id: str, data: SkillCreate) -> Skill:
        try:
            await self.profile_repository.ensure_exists(session, user_id)
            skill = await self.skill_repository.create(session, user_id, data)
            await session.commit()
            await session.refresh(skill)
            return skill
        except IntegrityError as exc:
            await session.rollback()
            raise SkillNameAlreadyExistsError from exc

    async def update_skill(
        self,
        session: AsyncSession,
        skill_id: UUID,
        user_id: str,
        data: SkillUpdate,
    ) -> Skill:
        skill = await self.get_skill(session, skill_id, user_id)
        try:
            skill = await self.skill_repository.update(session, skill, data)
            await session.commit()
            await session.refresh(skill)
            return skill
        except IntegrityError as exc:
            await session.rollback()
            raise SkillNameAlreadyExistsError from exc

    async def delete_skill(self, session: AsyncSession, skill_id: UUID, user_id: str) -> None:
        skill = await self.get_skill(session, skill_id, user_id)
        await self.skill_repository.delete(session, skill)
        await session.commit()

