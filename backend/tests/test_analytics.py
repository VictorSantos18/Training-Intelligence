from collections.abc import AsyncIterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.analytics.router import analytics_service
from app.modules.analytics.schemas import (
    AnalyticsOverview,
    AnalyticsStats,
    PainByRegionItem,
    RecentSessionItem,
    SessionsBySkillItem,
    TopExerciseItem,
)

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
SESSION_ID = "37d23d66-b1f2-4f41-bb03-4f90728451cd"
SKILL_ID = "2cc2e4e3-e961-46ff-9679-156c79ffed69"
EXERCISE_ID = "0e7d1ec7-9969-4f28-bf52-f3d611578ed1"
BODY_REGION_ID = "54b4db76-5ddd-44c6-9d2c-ce951cc7106d"


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


def test_get_analytics_overview_uses_current_user_id() -> None:
    client = make_client()
    analytics_service.get_overview = AsyncMock(return_value=make_overview())

    response = client.get("/analytics/overview")

    assert response.status_code == 200
    assert response.json()["stats"]["total_sessions"] == 4
    assert response.json()["sessions_by_skill"][0]["skill_name"] == "Front Lever"
    _, user_id = analytics_service.get_overview.await_args.args
    assert user_id == USER_ID
