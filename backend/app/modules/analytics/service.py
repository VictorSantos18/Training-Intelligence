from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schemas import AnalyticsOverview


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository | None = None) -> None:
        self.analytics_repository = analytics_repository or AnalyticsRepository()

    async def get_overview(self, session: AsyncSession, user_id: str) -> AnalyticsOverview:
        return await self.analytics_repository.get_overview(session, user_id)
