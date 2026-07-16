from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.exercises.router import exercise_service

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
EXERCISE_ID = "0e7d1ec7-9969-4f28-bf52-f3d611578ed1"
SKILL_ID = "2cc2e4e3-e961-46ff-9679-156c79ffed69"


def make_exercise(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": EXERCISE_ID,
        "skill_id": SKILL_ID,
        "name": "Front Lever Hold",
        "category": "HOLD",
        "measurement_type": "SECONDS",
        "is_active": True,
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


def test_create_exercise_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        "/exercises",
        json={
            "name": "Front Lever Hold",
            "category": "HOLD",
            "measurement_type": "SECONDS",
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
        },
    )

    assert response.status_code == 422


def test_create_exercise_uses_current_user_id() -> None:
    client = make_client()
    exercise_service.create_exercise = AsyncMock(return_value=make_exercise())

    response = client.post(
        "/exercises",
        json={
            "skill_id": SKILL_ID,
            "name": "Front Lever Hold",
            "category": "HOLD",
            "measurement_type": "SECONDS",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Front Lever Hold"
    _, user_id, payload = exercise_service.create_exercise.await_args.args
    assert user_id == USER_ID
    assert str(payload.skill_id) == SKILL_ID


def test_list_exercises_uses_current_user_id_and_filters() -> None:
    client = make_client()
    exercise_service.list_exercises = AsyncMock(return_value=[make_exercise()])

    response = client.get(f"/exercises?skill_id={SKILL_ID}&is_active=true")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Front Lever Hold"
    _, user_id = exercise_service.list_exercises.await_args.args
    kwargs = exercise_service.list_exercises.await_args.kwargs
    assert user_id == USER_ID
    assert str(kwargs["skill_id"]) == SKILL_ID
    assert kwargs["is_active"] is True


def test_get_exercise_uses_current_user_id() -> None:
    client = make_client()
    exercise_service.get_exercise = AsyncMock(return_value=make_exercise())

    response = client.get(f"/exercises/{EXERCISE_ID}")

    assert response.status_code == 200
    _, exercise_id, user_id = exercise_service.get_exercise.await_args.args
    assert str(exercise_id) == EXERCISE_ID
    assert user_id == USER_ID


def test_update_exercise_uses_current_user_id() -> None:
    client = make_client()
    exercise_service.update_exercise = AsyncMock(return_value=make_exercise(is_active=False))

    response = client.patch(f"/exercises/{EXERCISE_ID}", json={"is_active": False})

    assert response.status_code == 200
    _, exercise_id, user_id, payload = exercise_service.update_exercise.await_args.args
    assert str(exercise_id) == EXERCISE_ID
    assert user_id == USER_ID
    assert payload.is_active is False


def test_delete_exercise_deactivates_using_current_user_id() -> None:
    client = make_client()
    exercise_service.deactivate_exercise = AsyncMock(return_value=make_exercise(is_active=False))

    response = client.delete(f"/exercises/{EXERCISE_ID}")

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    _, exercise_id, user_id = exercise_service.deactivate_exercise.await_args.args
    assert str(exercise_id) == EXERCISE_ID
    assert user_id == USER_ID

