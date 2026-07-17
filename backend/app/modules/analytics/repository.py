from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_region import BodyRegion
from app.models.exercise import Exercise
from app.models.pain_record import PainRecord
from app.models.session_exercise import SessionExercise
from app.models.skill import Skill
from app.models.training_session import TrainingSession
from app.models.training_set import TrainingSet
from app.modules.analytics.schemas import (
    AnalyticsOverview,
    AnalyticsStats,
    PainByRegionItem,
    RecentSessionItem,
    SessionsBySkillItem,
    TopExerciseItem,
)
from app.modules.sessions.schemas import TrainingSessionStatus


def _int_value(value: Any) -> int:
    return int(value or 0)


def _float_value(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return round(float(value), 2)
    return round(float(value), 2)


def _float_zero(value: Any) -> float:
    return _float_value(value) or 0.0


class AnalyticsRepository:
    async def get_overview(self, session: AsyncSession, user_id: str) -> AnalyticsOverview:
        stats = await self._get_stats(session, user_id)
        return AnalyticsOverview(
            stats=stats,
            sessions_by_skill=await self._list_sessions_by_skill(session, user_id),
            recent_sessions=await self._list_recent_sessions(session, user_id),
            top_exercises=await self._list_top_exercises(session, user_id),
            pain_by_region=await self._list_pain_by_region(session, user_id),
        )

    async def _get_stats(self, session: AsyncSession, user_id: str) -> AnalyticsStats:
        session_stats = await session.execute(
            select(
                func.count(TrainingSession.id).label("total_sessions"),
                func.sum(
                    case(
                        (TrainingSession.status == TrainingSessionStatus.completed.value, 1),
                        else_=0,
                    )
                ).label("completed_sessions"),
                func.sum(
                    case(
                        (TrainingSession.status == TrainingSessionStatus.in_progress.value, 1),
                        else_=0,
                    )
                ).label("in_progress_sessions"),
                func.sum(
                    case(
                        (TrainingSession.status == TrainingSessionStatus.cancelled.value, 1),
                        else_=0,
                    )
                ).label("cancelled_sessions"),
                func.avg(TrainingSession.energy_before).label("average_energy_before"),
                func.avg(TrainingSession.sleep_hours).label("average_sleep_hours"),
            ).where(TrainingSession.user_id == user_id)
        )
        stats_row = session_stats.one()

        set_count = await session.execute(
            select(func.count(TrainingSet.id))
            .join(SessionExercise, TrainingSet.session_exercise_id == SessionExercise.id)
            .join(TrainingSession, SessionExercise.session_id == TrainingSession.id)
            .where(TrainingSession.user_id == user_id)
        )
        pain_count = await session.execute(
            select(func.count(PainRecord.id)).where(PainRecord.user_id == user_id)
        )

        return AnalyticsStats(
            total_sessions=_int_value(stats_row.total_sessions),
            completed_sessions=_int_value(stats_row.completed_sessions),
            in_progress_sessions=_int_value(stats_row.in_progress_sessions),
            cancelled_sessions=_int_value(stats_row.cancelled_sessions),
            total_sets=_int_value(set_count.scalar_one()),
            pain_records=_int_value(pain_count.scalar_one()),
            average_energy_before=_float_value(stats_row.average_energy_before),
            average_sleep_hours=_float_value(stats_row.average_sleep_hours),
        )

    async def _list_sessions_by_skill(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[SessionsBySkillItem]:
        result = await session.execute(
            select(
                TrainingSession.skill_id.label("skill_id"),
                Skill.name.label("skill_name"),
                func.count(TrainingSession.id).label("session_count"),
                func.sum(
                    case(
                        (TrainingSession.status == TrainingSessionStatus.completed.value, 1),
                        else_=0,
                    )
                ).label("completed_count"),
            )
            .outerjoin(Skill, TrainingSession.skill_id == Skill.id)
            .where(TrainingSession.user_id == user_id)
            .group_by(TrainingSession.skill_id, Skill.name)
            .order_by(sa.desc("session_count"), Skill.name.asc())
            .limit(6)
        )

        return [
            SessionsBySkillItem(
                skill_id=row.skill_id,
                skill_name=row.skill_name or "Sessao geral",
                session_count=_int_value(row.session_count),
                completed_count=_int_value(row.completed_count),
            )
            for row in result.all()
        ]

    async def _list_recent_sessions(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[RecentSessionItem]:
        result = await session.execute(
            select(
                TrainingSession.id,
                Skill.name.label("skill_name"),
                TrainingSession.status,
                TrainingSession.started_at,
                TrainingSession.finished_at,
            )
            .outerjoin(Skill, TrainingSession.skill_id == Skill.id)
            .where(TrainingSession.user_id == user_id)
            .order_by(TrainingSession.started_at.desc())
            .limit(5)
        )

        return [
            RecentSessionItem(
                id=row.id,
                skill_name=row.skill_name or "Sessao geral",
                status=row.status,
                started_at=row.started_at,
                finished_at=row.finished_at,
            )
            for row in result.all()
        ]

    async def _list_top_exercises(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[TopExerciseItem]:
        result = await session.execute(
            select(
                Exercise.id.label("exercise_id"),
                Exercise.name.label("exercise_name"),
                func.count(TrainingSet.id).label("set_count"),
                func.sum(case((TrainingSet.result == "SUCCESS", 1), else_=0)).label(
                    "success_count"
                ),
                func.coalesce(func.sum(TrainingSet.repetitions), 0).label("total_repetitions"),
                func.coalesce(func.sum(TrainingSet.duration_seconds), 0).label(
                    "total_duration_seconds"
                ),
            )
            .join(SessionExercise, TrainingSet.session_exercise_id == SessionExercise.id)
            .join(TrainingSession, SessionExercise.session_id == TrainingSession.id)
            .join(Exercise, SessionExercise.exercise_id == Exercise.id)
            .where(TrainingSession.user_id == user_id)
            .group_by(Exercise.id, Exercise.name)
            .order_by(sa.desc("set_count"), Exercise.name.asc())
            .limit(6)
        )

        return [
            TopExerciseItem(
                exercise_id=row.exercise_id,
                exercise_name=row.exercise_name,
                set_count=_int_value(row.set_count),
                success_count=_int_value(row.success_count),
                total_repetitions=_int_value(row.total_repetitions),
                total_duration_seconds=_float_zero(row.total_duration_seconds),
            )
            for row in result.all()
        ]

    async def _list_pain_by_region(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[PainByRegionItem]:
        result = await session.execute(
            select(
                BodyRegion.id.label("body_region_id"),
                BodyRegion.name.label("body_region_name"),
                func.count(PainRecord.id).label("record_count"),
                func.avg(PainRecord.intensity).label("average_intensity"),
                func.max(PainRecord.intensity).label("max_intensity"),
            )
            .join(BodyRegion, PainRecord.body_region_id == BodyRegion.id)
            .where(PainRecord.user_id == user_id)
            .group_by(BodyRegion.id, BodyRegion.name)
            .order_by(sa.desc("record_count"), sa.desc("average_intensity"))
            .limit(6)
        )

        return [
            PainByRegionItem(
                body_region_id=row.body_region_id,
                body_region_name=row.body_region_name,
                record_count=_int_value(row.record_count),
                average_intensity=_float_zero(row.average_intensity),
                max_intensity=_int_value(row.max_intensity),
            )
            for row in result.all()
        ]
