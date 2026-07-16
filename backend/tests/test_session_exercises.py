from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.session_exercises.router import session_exercise_service

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
SESSION_ID = "37d23d66-b1f2-4f41-bb03-4f90728451cd"
SESSION_EXERCISE_ID = "9be5475f-ae30-4213-8e42-83056a50ea53"
EXERCISE_ID = "0e7d1ec7-9969-4f28-bf52-f3d611578ed1"


def make_session_exercise(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": SESSION_EXERCISE_ID,
        "session_id": SESSION_ID,
        "exercise_id": EXERCISE_ID,
        "execution_order": 1,
        "notes": "Main attempt",
        "created_at": now,
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


def test_create_session_exercise_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        f"/sessions/{SESSION_ID}/exercises",
        json={
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
            "exercise_id": EXERCISE_ID,
            "execution_order": 1,
        },
    )

    assert response.status_code == 422


def test_create_session_exercise_uses_current_user_id() -> None:
    client = make_client()
    session_exercise_service.create_session_exercise = AsyncMock(
        return_value=make_session_exercise()
    )

    response = client.post(
        f"/sessions/{SESSION_ID}/exercises",
        json={
            "exercise_id": EXERCISE_ID,
            "execution_order": 1,
            "notes": "Main attempt",
        },
    )

    assert response.status_code == 201
    assert response.json()["execution_order"] == 1
    _, session_id, user_id, payload = (
        session_exercise_service.create_session_exercise.await_args.args
    )
    assert str(session_id) == SESSION_ID
    assert user_id == USER_ID
    assert str(payload.exercise_id) == EXERCISE_ID


def test_update_session_exercise_uses_current_user_id() -> None:
    client = make_client()
    session_exercise_service.update_session_exercise = AsyncMock(
        return_value=make_session_exercise(execution_order=2)
    )

    response = client.patch(
        f"/session-exercises/{SESSION_EXERCISE_ID}",
        json={"execution_order": 2},
    )

    assert response.status_code == 200
    _, session_exercise_id, user_id, payload = (
        session_exercise_service.update_session_exercise.await_args.args
    )
    assert str(session_exercise_id) == SESSION_EXERCISE_ID
    assert user_id == USER_ID
    assert payload.execution_order == 2


def test_delete_session_exercise_uses_current_user_id() -> None:
    client = make_client()
    session_exercise_service.delete_session_exercise = AsyncMock(return_value=None)

    response = client.delete(f"/session-exercises/{SESSION_EXERCISE_ID}")

    assert response.status_code == 204
    _, session_exercise_id, user_id = (
        session_exercise_service.delete_session_exercise.await_args.args
    )
    assert str(session_exercise_id) == SESSION_EXERCISE_ID
    assert user_id == USER_ID
