from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile


class ProfileRepository:
    async def get_by_id(self, session: AsyncSession, profile_id: str) -> Profile | None:
        result = await session.execute(select(Profile).where(Profile.id == profile_id))
        return result.scalar_one_or_none()

    async def ensure_exists(self, session: AsyncSession, profile_id: str) -> Profile:
        profile = await self.get_by_id(session, profile_id)
        if profile is not None:
            return profile

        profile = Profile(id=profile_id)
        session.add(profile)
        await session.flush()
        return profile

