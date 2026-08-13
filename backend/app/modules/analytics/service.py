from statistics import mean
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.exceptions import (
    AnalysisReportEmptyPeriodError,
    AnalysisReportNotFoundError,
    AnalysisReportSkillNotFoundError,
)
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schemas import (
    AnalysisReportGenerate,
    AnalysisReportListItem,
    AnalysisReportRead,
    AnalysisReportUpdate,
    AnalyticsOverview,
)
from app.modules.profiles.repository import ProfileRepository
from app.modules.skills.repository import SkillRepository


class AnalyticsService:
    def __init__(
        self,
        analytics_repository: AnalyticsRepository | None = None,
        profile_repository: ProfileRepository | None = None,
        skill_repository: SkillRepository | None = None,
    ) -> None:
        self.analytics_repository = analytics_repository or AnalyticsRepository()
        self.profile_repository = profile_repository or ProfileRepository()
        self.skill_repository = skill_repository or SkillRepository()

    async def get_overview(self, session: AsyncSession, user_id: str) -> AnalyticsOverview:
        return await self.analytics_repository.get_overview(session, user_id)

    async def list_reports(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 20,
    ) -> list[AnalysisReportListItem]:
        reports = await self.analytics_repository.list_reports(session, user_id, limit)
        return [AnalysisReportListItem.model_validate(report) for report in reports]

    async def get_report(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: str,
    ) -> AnalysisReportRead:
        report = await self.analytics_repository.get_report_by_id_and_user(
            session,
            report_id,
            user_id,
        )
        if report is None:
            raise AnalysisReportNotFoundError
        return AnalysisReportRead.model_validate(report)

    async def generate_report(
        self,
        session: AsyncSession,
        user_id: str,
        data: AnalysisReportGenerate,
    ) -> AnalysisReportRead:
        await self.profile_repository.ensure_exists(session, user_id)
        skill_name = await self._get_skill_name(session, data.skill_id, user_id)
        training_sessions = await self.analytics_repository.list_completed_sessions_for_report(
            session,
            user_id,
            period_start=data.period_start,
            period_end=data.period_end,
            skill_id=str(data.skill_id) if data.skill_id is not None else None,
        )
        if not training_sessions:
            raise AnalysisReportEmptyPeriodError

        summary_snapshot = self._build_summary_snapshot(training_sessions)
        filters = {
            "period_start": data.period_start.isoformat(),
            "period_end": data.period_end.isoformat(),
            "skill_id": str(data.skill_id) if data.skill_id is not None else None,
            "skill_name": skill_name,
            "status": "COMPLETED",
        }
        title = data.title or self._build_default_title(data, skill_name)
        generated_prompt = self._build_prompt(
            title=title,
            filters=filters,
            summary_snapshot=summary_snapshot,
            training_sessions=training_sessions,
        )

        report = await self.analytics_repository.create_report(
            session,
            user_id,
            skill_id=str(data.skill_id) if data.skill_id is not None else None,
            title=title,
            period_start=data.period_start,
            period_end=data.period_end,
            filters=filters,
            summary_snapshot=summary_snapshot,
            generated_prompt=generated_prompt,
            training_session_ids=[item["id"] for item in training_sessions],
        )
        await session.commit()
        loaded_report = await self.analytics_repository.get_report_by_id_and_user(
            session,
            UUID(report.id),
            user_id,
        )
        if loaded_report is None:
            raise AnalysisReportNotFoundError
        return AnalysisReportRead.model_validate(loaded_report)

    async def update_report(
        self,
        session: AsyncSession,
        report_id: UUID,
        user_id: str,
        data: AnalysisReportUpdate,
    ) -> AnalysisReportRead:
        report = await self.analytics_repository.get_report_by_id_and_user(
            session,
            report_id,
            user_id,
        )
        if report is None:
            raise AnalysisReportNotFoundError
        report = await self.analytics_repository.update_report(
            session,
            report,
            title=data.title,
            external_analysis=data.external_analysis,
            has_external_analysis_update="external_analysis" in data.model_fields_set,
        )
        await session.commit()
        loaded_report = await self.analytics_repository.get_report_by_id_and_user(
            session,
            UUID(report.id),
            user_id,
        )
        if loaded_report is None:
            raise AnalysisReportNotFoundError
        return AnalysisReportRead.model_validate(loaded_report)

    async def _get_skill_name(
        self,
        session: AsyncSession,
        skill_id: UUID | None,
        user_id: str,
    ) -> str | None:
        if skill_id is None:
            return None
        skill = await self.skill_repository.get_by_id_and_user(session, skill_id, user_id)
        if skill is None:
            raise AnalysisReportSkillNotFoundError
        return skill.name

    def _build_default_title(
        self,
        data: AnalysisReportGenerate,
        skill_name: str | None,
    ) -> str:
        scope = skill_name or "Todas as skills"
        return f"{scope} - {data.period_start.isoformat()} a {data.period_end.isoformat()}"

    def _build_summary_snapshot(
        self,
        training_sessions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sets = [
            training_set
            for training_session in training_sessions
            for exercise in training_session["exercises"]
            for training_set in exercise["sets"]
        ]
        pain_records = [
            pain_record
            for training_session in training_sessions
            for pain_record in training_session["pain_records"]
        ]
        rpe_values = [
            training_set["rpe"]
            for training_set in sets
            if training_set["rpe"] is not None
        ]
        energy_values = [
            training_session["energy_before"]
            for training_session in training_sessions
            if training_session["energy_before"] is not None
        ]
        sleep_values = [
            training_session["sleep_hours"]
            for training_session in training_sessions
            if training_session["sleep_hours"] is not None
        ]
        skills = sorted({training_session["skill_name"] for training_session in training_sessions})

        return {
            "total_sessions": len(training_sessions),
            "total_sets": len(sets),
            "total_repetitions": sum(training_set["repetitions"] or 0 for training_set in sets),
            "total_duration_seconds": round(
                sum(training_set["duration_seconds"] or 0 for training_set in sets),
                2,
            ),
            "average_rpe": round(mean(rpe_values), 2) if rpe_values else None,
            "average_energy_before": round(mean(energy_values), 2) if energy_values else None,
            "average_sleep_hours": round(mean(sleep_values), 2) if sleep_values else None,
            "max_pain_intensity": max(
                (pain_record["intensity"] for pain_record in pain_records),
                default=None,
            ),
            "pain_records_count": len(pain_records),
            "skills": skills,
            "sessions": training_sessions,
        }

    def _build_prompt(
        self,
        *,
        title: str,
        filters: dict[str, Any],
        summary_snapshot: dict[str, Any],
        training_sessions: list[dict[str, Any]],
    ) -> str:
        lines = [
            "# Análise de treino",
            "",
            "Você é um analista de treino especializado em calistenia e progressão de skills.",
            "Use exclusivamente os dados fornecidos abaixo e destaque claramente quando algum dado importante estiver",
            "ausente ou insuficiente para uma conclusão segura.",
            "",
            "Objetivo da análise:",
            "- avaliar o volume total, o volume por skill e o volume por exercício;",
            "- identificar sinais de fadiga, acúmulo de carga ou recuperação insuficiente;",
            "- relacionar RPE, sono, energia, descanso entre séries e dor/desconforto;",
            "- indicar se a próxima semana deve ser de progressão, manutenção, deload ou manter como está por hora;",
            "- sugerir ajustes objetivos em séries, repetições, tempo de isometria, descanso ou",
            "  escolha de exercícios, quando os dados sustentarem essa recomendação.",
            "",
            "Formato esperado da resposta:",
            "- resumo executivo curto;",
            "- leitura do volume e da intensidade;",
            "- leitura de fadiga, recuperação e dor;",
            "- decisão recomendada para a próxima semana;",
            "- plano prático de ajuste, com recomendações conservadoras e justificadas.",
            "",
            f"## Relatório: {title}",
            f"- Período: {filters['period_start']} a {filters['period_end']}",
            f"- Skill analisada: {filters['skill_name'] or 'Todas'}",
            "- Status considerado: somente sessões finalizadas",
            "",
            "## Resumo dos dados",
            f"- Sessões finalizadas: {summary_snapshot['total_sessions']}",
            f"- Séries registradas: {summary_snapshot['total_sets']}",
            f"- Repetições totais: {summary_snapshot['total_repetitions']}",
            f"- Tempo total em isometria/execução: {summary_snapshot['total_duration_seconds']}s",
            f"- RPE médio: {summary_snapshot['average_rpe']}",
            f"- Energia média antes do treino: {summary_snapshot['average_energy_before']}",
            f"- Sono médio: {summary_snapshot['average_sleep_hours']}h",
            f"- Dor máxima registrada: {summary_snapshot['max_pain_intensity']}",
            "",
            "## Sessões analisadas",
        ]
        for training_session in training_sessions:
            lines.extend(
                [
                    "",
                    f"### {training_session['skill_name']} - {training_session['started_at']}",
                    f"- Sono: {training_session['sleep_hours']}h",
                    f"- Energia: {training_session['energy_before']}/10",
                    f"- Notas pós-sessão: {training_session['notes_after'] or 'Sem notas'}",
                    "",
                    "Exercícios realizados:",
                ]
            )
            for exercise in training_session["exercises"]:
                lines.append(
                    f"- {exercise['exercise_name']} "
                    f"(ordem {exercise['execution_order']}): {exercise['notes'] or 'sem notas'}"
                )
                for training_set in exercise["sets"]:
                    lines.append(
                        "  - Set "
                        f"{training_set['set_number']}: reps={training_set['repetitions']}, "
                        f"duração={training_set['duration_seconds']}s, "
                        f"RPE={training_set['rpe']}, "
                        f"resultado={training_set['result']}, "
                        f"descanso={training_set['rest_seconds']}s, "
                        f"notas={training_set['notes'] or 'sem notas'}"
                    )
            if training_session["pain_records"]:
                lines.append("")
                lines.append("Registros de dor/desconforto:")
                for pain_record in training_session["pain_records"]:
                    lines.append(
                        f"- {pain_record['body_region_name']}: "
                        f"intensidade {pain_record['intensity']}/10, "
                        f"momento={pain_record['moment']}, "
                        f"descrição={pain_record['description'] or 'sem descrição'}, "
                        f"notas={pain_record['notes'] or 'sem notas'}"
                    )
        return "\n".join(lines)
