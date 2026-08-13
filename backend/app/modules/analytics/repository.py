from decimal import Decimal
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.body_region import BodyRegion
from app.models.exercise import Exercise
from app.models.pain_record import PainRecord
from app.models.session_exercise import SessionExercise
from app.models.skill import Skill
from app.models.training_analysis_report import (
    TrainingAnalysisReport,
    TrainingAnalysisReportSession,
)
from app.models.training_session import TrainingSession
from app.models.training_set import TrainingSet
from app.modules.analytics.schemas import (
    AnalysisReportStatus,
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

    async def list_reports(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> list[TrainingAnalysisReport]:
        result = await session.execute(
            select(TrainingAnalysisReport)
            .where(TrainingAnalysisReport.user_id == user_id)
            .order_by(TrainingAnalysisReport.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_report_by_id_and_user(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: str,
    ) -> TrainingAnalysisReport | None:
        result = await session.execute(
            select(TrainingAnalysisReport)
            .options(selectinload(TrainingAnalysisReport.sessions))
            .where(
                TrainingAnalysisReport.id == str(report_id),
                TrainingAnalysisReport.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_report(
        self,
        session: AsyncSession,
        user_id: str,
        *,
        skill_id: str | None,
        title: str,
        period_start: Any,
        period_end: Any,
        filters: dict[str, Any],
        summary_snapshot: dict[str, Any],
        generated_prompt: str,
        training_session_ids: list[str],
    ) -> TrainingAnalysisReport:
        analysis_report = TrainingAnalysisReport(
            user_id=user_id,
            skill_id=skill_id,
            title=title,
            period_start=period_start,
            period_end=period_end,
            filters=filters,
            summary_snapshot=summary_snapshot,
            generated_prompt=generated_prompt,
        )
        session.add(analysis_report)
        await session.flush()

        for training_session_id in training_session_ids:
            session.add(
                TrainingAnalysisReportSession(
                    analysis_report_id=analysis_report.id,
                    training_session_id=training_session_id,
                )
            )

        await session.flush()
        return analysis_report

    async def update_report(
        self,
        session: AsyncSession,
        report: TrainingAnalysisReport,
        *,
        title: str | None = None,
        external_analysis: str | None = None,
        has_external_analysis_update: bool = False,
    ) -> TrainingAnalysisReport:
        if title is not None:
            report.title = title
        if has_external_analysis_update:
            report.external_analysis = external_analysis
            report.status = (
                AnalysisReportStatus.analysis_saved.value
                if external_analysis
                else AnalysisReportStatus.prompt_generated.value
            )
        await session.flush()
        return report

    async def list_completed_sessions_for_report(
        self,
        session: AsyncSession,
        user_id: str,
        *,
        period_start: Any,
        period_end: Any,
        skill_id: str | None = None,
    ) -> list[dict[str, Any]]:
        session_query = (
            select(
                TrainingSession.id,
                TrainingSession.skill_id,
                Skill.name.label("skill_name"),
                TrainingSession.started_at,
                TrainingSession.finished_at,
                TrainingSession.sleep_hours,
                TrainingSession.energy_before,
                TrainingSession.notes_after,
            )
            .outerjoin(Skill, TrainingSession.skill_id == Skill.id)
            .where(
                TrainingSession.user_id == user_id,
                TrainingSession.status == TrainingSessionStatus.completed.value,
                sa.cast(TrainingSession.started_at, sa.Date) >= period_start,
                sa.cast(TrainingSession.started_at, sa.Date) <= period_end,
            )
            .order_by(TrainingSession.started_at.asc())
        )
        if skill_id is not None:
            session_query = session_query.where(TrainingSession.skill_id == skill_id)

        session_rows = (await session.execute(session_query)).all()
        session_items = [
            {
                "id": row.id,
                "skill_id": row.skill_id,
                "skill_name": row.skill_name or "Sessao geral",
                "started_at": row.started_at.isoformat(),
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "sleep_hours": _float_value(row.sleep_hours),
                "energy_before": row.energy_before,
                "notes_after": row.notes_after,
                "exercises": [],
                "pain_records": [],
            }
            for row in session_rows
        ]
        session_ids = [item["id"] for item in session_items]
        if not session_ids:
            return session_items

        session_by_id = {item["id"]: item for item in session_items}
        session_exercise_ids: list[str] = []
        exercise_by_id: dict[str, dict[str, Any]] = {}
        exercise_rows = await session.execute(
            select(
                SessionExercise.id,
                SessionExercise.session_id,
                SessionExercise.execution_order,
                SessionExercise.notes,
                Exercise.name.label("exercise_name"),
            )
            .join(Exercise, SessionExercise.exercise_id == Exercise.id)
            .where(SessionExercise.session_id.in_(session_ids))
            .order_by(SessionExercise.session_id.asc(), SessionExercise.execution_order.asc())
        )
        for row in exercise_rows.all():
            exercise_item = {
                "session_exercise_id": row.id,
                "exercise_name": row.exercise_name,
                "execution_order": row.execution_order,
                "notes": row.notes,
                "sets": [],
            }
            session_by_id[row.session_id]["exercises"].append(exercise_item)
            session_exercise_ids.append(row.id)
            exercise_by_id[row.id] = exercise_item

        if session_exercise_ids:
            set_rows = await session.execute(
                select(
                    TrainingSet.id,
                    TrainingSet.session_exercise_id,
                    TrainingSet.set_number,
                    TrainingSet.repetitions,
                    TrainingSet.duration_seconds,
                    TrainingSet.assistance_level,
                    TrainingSet.rpe,
                    TrainingSet.result,
                    TrainingSet.technical_quality,
                    TrainingSet.rest_seconds,
                    TrainingSet.notes,
                )
                .where(TrainingSet.session_exercise_id.in_(session_exercise_ids))
                .order_by(TrainingSet.session_exercise_id.asc(), TrainingSet.set_number.asc())
            )
            for row in set_rows.all():
                exercise_by_id[row.session_exercise_id]["sets"].append(
                    {
                        "id": row.id,
                        "set_number": row.set_number,
                        "repetitions": row.repetitions,
                        "duration_seconds": _float_value(row.duration_seconds),
                        "assistance_level": _float_value(row.assistance_level),
                        "rpe": _float_value(row.rpe),
                        "result": row.result,
                        "technical_quality": row.technical_quality,
                        "rest_seconds": row.rest_seconds,
                        "notes": row.notes,
                    }
                )

        pain_rows = await session.execute(
            select(
                PainRecord.id,
                PainRecord.training_session_id,
                PainRecord.training_set_id,
                PainRecord.occurred_at,
                PainRecord.moment,
                PainRecord.intensity,
                PainRecord.description,
                PainRecord.notes,
                BodyRegion.name.label("body_region_name"),
            )
            .join(BodyRegion, PainRecord.body_region_id == BodyRegion.id)
            .where(PainRecord.training_session_id.in_(session_ids))
            .order_by(PainRecord.occurred_at.asc())
        )
        for row in pain_rows.all():
            if row.training_session_id not in session_by_id:
                continue
            session_by_id[row.training_session_id]["pain_records"].append(
                {
                    "id": row.id,
                    "training_set_id": row.training_set_id,
                    "occurred_at": row.occurred_at.isoformat(),
                    "moment": row.moment,
                    "body_region_name": row.body_region_name,
                    "intensity": row.intensity,
                    "description": row.description,
                    "notes": row.notes,
                }
            )

        return session_items

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
            .limit(3)
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
