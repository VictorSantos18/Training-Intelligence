from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_region import BodyRegion
from app.modules.body_regions.repository import BodyRegionRepository


class BodyRegionService:
    def __init__(self, body_region_repository: BodyRegionRepository | None = None) -> None:
        self.body_region_repository = body_region_repository or BodyRegionRepository()

    async def list_body_regions(self, session: AsyncSession) -> list[BodyRegion]:
        return await self.body_region_repository.list_active(session)
