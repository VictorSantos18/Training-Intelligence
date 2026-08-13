from collections.abc import AsyncIterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.analytics.router import analytics_service
from app.modules.analytics.schemas import (
    AnalysisReportListItem,
    AnalysisReportRead,
    AnalyticsOverview,
    AnalyticsStats,
    PainByRegionItem,
    RecentSessionItem,
    SessionsBySkillItem,
    TopExerciseItem,
)
from app.modules.analytics.service import AnalyticsService

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
SESSION_ID = "37d23d66-b1f2-4f41-bb03-4f90728451cd"
SKILL_ID = "2cc2e4e3-e961-46ff-9679-156c79ffed69"
EXERCISE_ID = "0e7d1ec7-9969-4f28-bf52-f3d611578ed1"
BODY_REGION_ID = "54b4db76-5ddd-44c6-9d2c-ce951cc7106d"
REPORT_ID = "8cb19108-c8c7-426e-a8d7-d1f5da71a44b"


async def override_current_user() -> CurrentUser:
    return CurrentUser(
        id=USER_ID,
        email="person@example.com",
        role="authenticated",
        claims={},
    )


async def override_db_session() -> AsyncIterator[object]:
    yield object()


def make_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db_session] = override_db_session
    return TestClient(app)


def make_overview() -> AnalyticsOverview:
    now = datetime.now(UTC)
    return AnalyticsOverview(
        stats=AnalyticsStats(
            total_sessions=4,
            completed_sessions=3,
            in_progress_sessions=1,
            cancelled_sessions=0,
            total_sets=12,
            pain_records=2,
            average_energy_before=7.5,
            average_sleep_hours=7.25,
        ),
        sessions_by_skill=[
            SessionsBySkillItem(
                skill_id=SKILL_ID,
                skill_name="Front Lever",
                session_count=4,
                completed_count=3,
            )
        ],
        recent_sessions=[
            RecentSessionItem(
                id=SESSION_ID,
                skill_name="Front Lever",
                status="COMPLETED",
                started_at=now,
                finished_at=now,
            )
        ],
        top_exercises=[
            TopExerciseItem(
                exercise_id=EXERCISE_ID,
                exercise_name="Front Lever Hold",
                set_count=8,
                success_count=6,
                total_repetitions=0,
                total_duration_seconds=120.0,
            )
        ],
        pain_by_region=[
            PainByRegionItem(
                body_region_id=BODY_REGION_ID,
                body_region_name="Ombro direito",
                record_count=2,
                average_intensity=3.5,
                max_intensity=5,
            )
        ],
    )


def make_report(**overrides: object) -> AnalysisReportRead:
    now = datetime.now(UTC)
    values = {
        "id": REPORT_ID,
        "skill_id": SKILL_ID,
        "title": "Front Lever - 2026-07-13 a 2026-07-19",
        "period_start": "2026-07-13",
        "period_end": "2026-07-19",
        "filters": {
            "period_start": "2026-07-13",
            "period_end": "2026-07-19",
            "skill_id": SKILL_ID,
            "skill_name": "Front Lever",
            "status": "COMPLETED",
        },
        "summary_snapshot": {
            "total_sessions": 2,
            "total_sets": 12,
            "sessions": [],
        },
        "generated_prompt": "# Análise de treino",
        "external_analysis": None,
        "status": "PROMPT_GENERATED",
        "created_at": now,
        "updated_at": now,
        "sessions": [],
    }
    values.update(overrides)
    return AnalysisReportRead.model_validate(values)


def make_report_item(**overrides: object) -> AnalysisReportListItem:
    report = make_report(**overrides)
    return AnalysisReportListItem.model_validate(report)


def test_get_analytics_overview_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.get_overview = AsyncMock(return_value=make_overview())

    response = client.get("/analytics/overview")

    assert response.status_code == 200
    assert response.json()["stats"]["total_sessions"] == 4
    assert response.json()["sessions_by_skill"][0]["skill_name"] == "Front Lever"
    _, user_id = analytics_service.get_overview.await_args.args
    assert user_id == USER_ID


def test_list_analysis_reports_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.list_reports = AsyncMock(return_value=[make_report_item()])

    response = client.get("/analytics/reports")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Front Lever - 2026-07-13 a 2026-07-19"
    _, user_id, limit = analytics_service.list_reports.await_args.args
    assert user_id == USER_ID
    assert limit == 20


def test_generate_analysis_report_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        "/analytics/reports",
        json={
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
            "period_start": "2026-07-13",
            "period_end": "2026-07-19",
        },
    )

    assert response.status_code == 422


def test_generate_analysis_report_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.generate_report = AsyncMock(return_value=make_report())

    response = client.post(
        "/analytics/reports",
        json={
            "period_start": "2026-07-13",
            "period_end": "2026-07-19",
            "skill_id": SKILL_ID,
        },
    )

    assert response.status_code == 201
    assert response.json()["generated_prompt"] == "# Análise de treino"
    _, user_id, payload = analytics_service.generate_report.await_args.args
    assert user_id == USER_ID
    assert str(payload.skill_id) == SKILL_ID


def test_get_analysis_report_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.get_report = AsyncMock(return_value=make_report())

    response = client.get(f"/analytics/reports/{REPORT_ID}")

    assert response.status_code == 200
    _, report_id, user_id = analytics_service.get_report.await_args.args
    assert str(report_id) == REPORT_ID
    assert user_id == USER_ID


def test_update_analysis_report_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.update_report = AsyncMock(
        return_value=make_report(
            external_analysis="Manter volume e observar ombro.",
            status="ANALYSIS_SAVED",
        )
    )

    response = client.patch(
        f"/analytics/reports/{REPORT_ID}",
        json={"external_analysis": "Manter volume e observar ombro."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ANALYSIS_SAVED"
    _, report_id, user_id, payload = analytics_service.update_report.await_args.args
    assert str(report_id) == REPORT_ID
    assert user_id == USER_ID
    assert payload.external_analysis == "Manter volume e observar ombro."


def test_generated_prompt_formats_rest_and_missing_duration() -> None:
    service = AnalyticsService()

    prompt = service._build_prompt(
        title="Front Lever - semana",
        filters={
            "period_start": "2026-08-03",
            "period_end": "2026-08-10",
            "skill_name": "Front Lever",
        },
        summary_snapshot={
            "total_sessions": 1,
            "total_sets": 1,
            "total_repetitions": 2,
            "total_duration_seconds": 0,
            "average_rpe": 7,
            "average_energy_before": 8,
            "average_sleep_hours": 7,
            "max_pain_intensity": None,
        },
        training_sessions=[
            {
                "skill_name": "Front Lever",
                "started_at": "2026-08-10T20:35:00+00:00",
                "sleep_hours": 7,
                "energy_before": 8,
                "notes_after": None,
                "exercises": [
                    {
                        "exercise_name": "Front Lever Pull Up",
                        "execution_order": 1,
                        "notes": None,
                        "sets": [
                            {
                                "set_number": 1,
                                "repetitions": 2,
                                "duration_seconds": None,
                                "rpe": 7,
                                "result": "SUCCESS",
                                "rest_seconds": 180,
                                "notes": None,
                            }
                        ],
                    }
                ],
                "pain_records": [],
            }
        ],
    )

    assert "duração=não registrada" in prompt
    assert "descanso=3:00 min" in prompt
    assert "Tempo total em isometria/execução: não registrado" in prompt
    assert 'crie a seção "Resumo para salvar no app"' in prompt
    assert "Essa seção deve ser curta, direta e acionável" in prompt
