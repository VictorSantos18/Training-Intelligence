from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.training_session import TrainingSession
from app.modules.profiles.repository import ProfileRepository
from app.modules.sessions.exceptions import (
    TrainingSessionClosedError,
    TrainingSessionInvalidFinishError,
    TrainingSessionNotFoundError,
    TrainingSessionSkillNotFoundError,
)
from app.modules.sessions.repository import TrainingSessionRepository
from app.modules.sessions.schemas import (
    TrainingSessionCreate,
    TrainingSessionFinish,
    TrainingSessionStatus,
    TrainingSessionUpdate,
)
from app.modules.skills.repository import SkillRepository


class TrainingSessionService:
    def __init__(
        self,
        training_session_repository: TrainingSessionRepository | None = None,
        profile_repository: ProfileRepository | None = None,
        skill_repository: SkillRepository | None = None,
    ) -> None:
        self.training_session_repository = (
            training_session_repository or TrainingSessionRepository()
        )
        self.profile_repository = profile_repository or ProfileRepository()
        self.skill_repository = skill_repository or SkillRepository()

    async def list_training_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        skill_id: UUID | None = None,
        status: TrainingSessionStatus | None = None,
    ) -> list[TrainingSession]:
        return await self.training_session_repository.list_by_user(
            session,
            user_id,
            skill_id,
            status,
        )

    async def get_training_session(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
    ) -> TrainingSession:
        training_session = await self.training_session_repository.get_by_id_and_user(
            session,
            training_session_id,
            user_id,
        )
        if training_session is None:
            raise TrainingSessionNotFoundError
        return training_session

    async def create_training_session(
        self,
        session: AsyncSession,
        user_id: str,
        data: TrainingSessionCreate,
    ) -> TrainingSession:
        await self.profile_repository.ensure_exists(session, user_id)
        await self._ensure_skill_belongs_to_user(session, data.skill_id, user_id)
        training_session = await self.training_session_repository.create(session, user_id, data)
        await session.commit()
        await session.refresh(training_session)
        return training_session

    async def update_training_session(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
        data: TrainingSessionUpdate,
    ) -> TrainingSession:
        training_session = await self.get_training_session(session, training_session_id, user_id)
        self._ensure_open(training_session)
        if "skill_id" in data.model_fields_set:
            await self._ensure_skill_belongs_to_user(session, data.skill_id, user_id)
        training_session = await self.training_session_repository.update(
            session,
            training_session,
            data,
        )
        await session.commit()
        await session.refresh(training_session)
        return training_session

    async def finish_training_session(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
        data: TrainingSessionFinish,
    ) -> TrainingSession:
        training_session = await self.get_training_session(session, training_session_id, user_id)
        self._ensure_open(training_session)
        if data.finished_at is None:
            data.finished_at = datetime.now(UTC)
        if data.finished_at <= training_session.started_at:
            raise TrainingSessionInvalidFinishError
        training_session = await self.training_session_repository.finish(
            session,
            training_session,
            data,
        )
        await session.commit()
        await session.refresh(training_session)
        return training_session

    async def cancel_training_session(
        self,
        session: AsyncSession,
        training_session_id: UUID,
        user_id: str,
    ) -> TrainingSession:
        training_session = await self.get_training_session(session, training_session_id, user_id)
        self._ensure_open(training_session)
        training_session = await self.training_session_repository.cancel(session, training_session)
        await session.commit()
        await session.refresh(training_session)
        return training_session

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
            raise TrainingSessionSkillNotFoundError

    def _ensure_open(self, training_session: TrainingSession) -> None:
        if training_session.status != TrainingSessionStatus.in_progress.value:
            raise TrainingSessionClosedError
