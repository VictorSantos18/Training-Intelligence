from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pain_record import PainRecord
from app.models.training_set import TrainingSet
from app.modules.pain_records.exceptions import (
    PainRecordContextMismatchError,
    PainRecordNotFoundError,
    PainRecordTrainingSessionNotFoundError,
    PainRecordTrainingSetNotFoundError,
    PainRecordTrainingSetRequiredError,
)
from app.modules.pain_records.repository import PainRecordRepository
from app.modules.pain_records.schemas import PainRecordCreate, PainRecordMoment, PainRecordUpdate
from app.modules.sessions.repository import TrainingSessionRepository
from app.modules.training_sets.repository import TrainingSetRepository


class PainRecordService:
    def __init__(
        self,
        pain_record_repository: PainRecordRepository | None = None,
        training_session_repository: TrainingSessionRepository | None = None,
        training_set_repository: TrainingSetRepository | None = None,
    ) -> None:
        self.pain_record_repository = pain_record_repository or PainRecordRepository()
        self.training_session_repository = (
            training_session_repository or TrainingSessionRepository()
        )
        self.training_set_repository = training_set_repository or TrainingSetRepository()

    async def list_pain_records(
        self,
        session: AsyncSession,
        user_id: str,
        training_session_id: UUID | None = None,
        training_set_id: UUID | None = None,
    ) -> list[PainRecord]:
        return await self.pain_record_repository.list_by_user(
            session,
            user_id,
            training_session_id,
            training_set_id,
        )

    async def create_pain_record(
        self,
        session: AsyncSession,
        user_id: str,
        data: PainRecordCreate,
    ) -> PainRecord:
        training_session_id = await self._resolve_training_session_id(session, user_id, data)
        pain_record = await self.pain_record_repository.create(
            session,
            user_id,
            training_session_id,
            data,
        )
        await session.commit()
        await session.refresh(pain_record)
        return pain_record

    async def get_pain_record(
        self,
        session: AsyncSession,
        pain_record_id: UUID,
        user_id: str,
    ) -> PainRecord:
        pain_record = await self.pain_record_repository.get_by_id_and_user(
            session,
            pain_record_id,
            user_id,
        )
        if pain_record is None:
            raise PainRecordNotFoundError
        return pain_record

    async def update_pain_record(
        self,
        session: AsyncSession,
        pain_record_id: UUID,
        user_id: str,
        data: PainRecordUpdate,
    ) -> PainRecord:
        pain_record = await self.get_pain_record(session, pain_record_id, user_id)
        if data.moment == PainRecordMoment.during_set and pain_record.training_set_id is None:
            raise PainRecordTrainingSetRequiredError

        pain_record = await self.pain_record_repository.update(session, pain_record, data)
        await session.commit()
        await session.refresh(pain_record)
        return pain_record

    async def delete_pain_record(
        self,
        session: AsyncSession,
        pain_record_id: UUID,
        user_id: str,
    ) -> None:
        pain_record = await self.get_pain_record(session, pain_record_id, user_id)
        await self.pain_record_repository.delete(session, pain_record)
        await session.commit()

    async def _resolve_training_session_id(
        self,
        session: AsyncSession,
        user_id: str,
        data: PainRecordCreate,
    ) -> str:
        training_set: TrainingSet | None = None
        if data.training_set_id is not None:
            training_set = await self.training_set_repository.get_by_id_and_user(
                session,
                data.training_set_id,
                user_id,
            )
            if training_set is None:
                raise PainRecordTrainingSetNotFoundError
            await session.refresh(training_set, attribute_names=["session_exercise"])
            resolved_training_session_id = training_set.session_exercise.session_id
        elif data.training_session_id is not None:
            resolved_training_session_id = str(data.training_session_id)
        else:
            raise PainRecordTrainingSessionNotFoundError

        if data.training_session_id is not None:
            training_session = await self.training_session_repository.get_by_id_and_user(
                session,
                data.training_session_id,
                user_id,
            )
            if training_session is None:
                raise PainRecordTrainingSessionNotFoundError
            if str(data.training_session_id) != resolved_training_session_id:
                raise PainRecordContextMismatchError

        return resolved_training_session_id
