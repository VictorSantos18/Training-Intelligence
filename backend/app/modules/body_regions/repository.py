from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_region import BodyRegion


class BodyRegionRepository:
    async def list_active(self, session: AsyncSession) -> list[BodyRegion]:
        result = await session.execute(
            select(BodyRegion)
            .where(BodyRegion.is_active.is_(True))
            .order_by(BodyRegion.name.asc())
        )
        return list(result.scalars().all())

    async def get_active_by_id(
        self,
        session: AsyncSession,
        body_region_id: UUID,
    ) -> BodyRegion | None:
        result = await session.execute(
            select(BodyRegion).where(
                BodyRegion.id == str(body_region_id),
                BodyRegion.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()
