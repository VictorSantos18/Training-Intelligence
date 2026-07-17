from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.training_sets.router import training_set_service

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
SESSION_EXERCISE_ID = "9be5475f-ae30-4213-8e42-83056a50ea53"
TRAINING_SET_ID = "01ce428b-ae51-42ce-ad8f-b6e57ba73da2"


def make_training_set(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": TRAINING_SET_ID,
        "session_exercise_id": SESSION_EXERCISE_ID,
        "set_number": 1,
        "repetitions": 1,
        "duration_seconds": Decimal("8.50"),
        "assistance_level": None,
        "rpe": Decimal("8.5"),
        "pain_during": 1,
        "result": "SUCCESS",
        "technical_quality": "GOOD",
        "rest_seconds": 180,
        "notes": "Solid hold",
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


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


def test_create_training_set_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        f"/session-exercises/{SESSION_EXERCISE_ID}/sets",
        json={
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
            "set_number": 1,
            "duration_seconds": 8.5,
            "result": "SUCCESS",
        },
    )

    assert response.status_code == 422


def test_create_training_set_uses_current_user_id() -> None:
    client = make_client()
    training_set_service.create_training_set = AsyncMock(return_value=make_training_set())

    response = client.post(
        f"/session-exercises/{SESSION_EXERCISE_ID}/sets",
        json={
            "set_number": 1,
            "duration_seconds": 8.5,
            "rpe": 8.5,
            "pain_during": 1,
            "result": "SUCCESS",
            "technical_quality": "GOOD",
            "rest_seconds": 180,
        },
    )

    assert response.status_code == 201
    assert response.json()["set_number"] == 1
    _, session_exercise_id, user_id, payload = (
        training_set_service.create_training_set.await_args.args
    )
    assert str(session_exercise_id) == SESSION_EXERCISE_ID
    assert user_id == USER_ID
    assert payload.result == "SUCCESS"


def test_list_training_sets_uses_current_user_id() -> None:
    client = make_client()
    training_set_service.list_training_sets = AsyncMock(return_value=[make_training_set()])

    response = client.get(f"/session-exercises/{SESSION_EXERCISE_ID}/sets")

    assert response.status_code == 200
    assert response.json()[0]["id"] == TRAINING_SET_ID
    _, session_exercise_id, user_id = training_set_service.list_training_sets.await_args.args
    assert str(session_exercise_id) == SESSION_EXERCISE_ID
    assert user_id == USER_ID


def test_create_training_set_requires_metric_when_not_skipped() -> None:
    client = make_client()

    response = client.post(
        f"/session-exercises/{SESSION_EXERCISE_ID}/sets",
        json={
            "set_number": 1,
            "result": "SUCCESS",
        },
    )

    assert response.status_code == 422


def test_update_training_set_uses_current_user_id() -> None:
    client = make_client()
    training_set_service.update_training_set = AsyncMock(
        return_value=make_training_set(rpe=Decimal("9.0"))
    )

    response = client.patch(f"/sets/{TRAINING_SET_ID}", json={"rpe": 9.0})

    assert response.status_code == 200
    _, training_set_id, user_id, payload = training_set_service.update_training_set.await_args.args
    assert str(training_set_id) == TRAINING_SET_ID
    assert user_id == USER_ID
    assert payload.rpe == Decimal("9.0")


def test_delete_training_set_uses_current_user_id() -> None:
    client = make_client()
    training_set_service.delete_training_set = AsyncMock(return_value=None)

    response = client.delete(f"/sets/{TRAINING_SET_ID}")

    assert response.status_code == 204
    _, training_set_id, user_id = training_set_service.delete_training_set.await_args.args
    assert str(training_set_id) == TRAINING_SET_ID
    assert user_id == USER_ID
