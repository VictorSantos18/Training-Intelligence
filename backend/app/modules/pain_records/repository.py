from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pain_record import PainRecord
from app.modules.pain_records.schemas import PainRecordCreate, PainRecordUpdate


class PainRecordRepository:
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: str,
        training_session_id: UUID | None = None,
        training_set_id: UUID | None = None,
    ) -> list[PainRecord]:
        query = select(PainRecord).where(PainRecord.user_id == user_id)
        if training_session_id is not None:
            query = query.where(PainRecord.training_session_id == str(training_session_id))
        if training_set_id is not None:
            query = query.where(PainRecord.training_set_id == str(training_set_id))

        result = await session.execute(query.order_by(PainRecord.occurred_at.desc()))
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        session: AsyncSession,
        pain_record_id: UUID,
        user_id: str,
    ) -> PainRecord | None:
        result = await session.execute(
            select(PainRecord).where(
                PainRecord.id == str(pain_record_id),
                PainRecord.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        session: AsyncSession,
        user_id: str,
        training_session_id: str,
        data: PainRecordCreate,
    ) -> PainRecord:
        values = {
            "user_id": user_id,
            "training_session_id": training_session_id,
            "training_set_id": str(data.training_set_id) if data.training_set_id else None,
            "body_region_id": str(data.body_region_id),
            "side": data.side.value,
            "moment": data.moment.value,
            "intensity": data.intensity,
            "description": data.description,
            "notes": data.notes,
        }
        if data.occurred_at is not None:
            values["occurred_at"] = data.occurred_at

        pain_record = PainRecord(**values)
        session.add(pain_record)
        await session.flush()
        return pain_record

    async def update(
        self,
        session: AsyncSession,
        pain_record: PainRecord,
        data: PainRecordUpdate,
    ) -> PainRecord:
        values = data.model_dump(exclude_unset=True)
        for field in ("side", "moment"):
            if field in values and values[field] is not None:
                values[field] = values[field].value

        for field, value in values.items():
            setattr(pain_record, field, value)

        await session.flush()
        return pain_record

    async def delete(self, session: AsyncSession, pain_record: PainRecord) -> None:
        await session.delete(pain_record)
        await session.flush()
