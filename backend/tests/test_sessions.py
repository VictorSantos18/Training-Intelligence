from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.sessions.exceptions import (
    TrainingSessionClosedError,
    TrainingSessionInvalidFinishError,
)
from app.modules.sessions.router import training_session_service
from app.modules.sessions.schemas import TrainingSessionFinish, TrainingSessionUpdate
from app.modules.sessions.service import TrainingSessionService

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
SESSION_ID = "37d23d66-b1f2-4f41-bb03-4f90728451cd"
SKILL_ID = "2cc2e4e3-e961-46ff-9679-156c79ffed69"


def make_training_session(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": SESSION_ID,
        "skill_id": SKILL_ID,
        "started_at": now,
        "finished_at": None,
        "sleep_hours": Decimal("7.50"),
        "energy_before": 7,
        "notes_after": None,
        "status": "IN_PROGRESS",
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


def make_db_session() -> SimpleNamespace:
    return SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock())


def test_create_session_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        "/sessions",
        json={
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
            "started_at": "2026-07-16T18:00:00-03:00",
        },
    )

    assert response.status_code == 422


def test_create_session_uses_current_user_id() -> None:
    client = make_client()
    training_session_service.create_training_session = AsyncMock(
        return_value=make_training_session()
    )

    response = client.post(
        "/sessions",
        json={
            "skill_id": SKILL_ID,
            "started_at": "2026-07-16T18:00:00-03:00",
            "sleep_hours": 7.5,
            "energy_before": 8,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "IN_PROGRESS"
    _, user_id, payload = training_session_service.create_training_session.await_args.args
    assert user_id == USER_ID
    assert str(payload.skill_id) == SKILL_ID


def test_list_sessions_uses_current_user_id_and_filters() -> None:
    client = make_client()
    training_session_service.list_training_sessions = AsyncMock(
        return_value=[make_training_session()]
    )

    response = client.get(f"/sessions?skill_id={SKILL_ID}&status=IN_PROGRESS")

    assert response.status_code == 200
    _, user_id = training_session_service.list_training_sessions.await_args.args
    kwargs = training_session_service.list_training_sessions.await_args.kwargs
    assert user_id == USER_ID
    assert str(kwargs["skill_id"]) == SKILL_ID
    assert kwargs["status"] == "IN_PROGRESS"


def test_get_session_uses_current_user_id() -> None:
    client = make_client()
    training_session_service.get_training_session = AsyncMock(
        return_value=make_training_session()
    )

    response = client.get(f"/sessions/{SESSION_ID}")

    assert response.status_code == 200
    _, session_id, user_id = training_session_service.get_training_session.await_args.args
    assert str(session_id) == SESSION_ID
    assert user_id == USER_ID


def test_update_session_uses_current_user_id() -> None:
    client = make_client()
    training_session_service.update_training_session = AsyncMock(
        return_value=make_training_session(energy_before=9)
    )

    response = client.patch(f"/sessions/{SESSION_ID}", json={"energy_before": 9})

    assert response.status_code == 200
    _, session_id, user_id, payload = (
        training_session_service.update_training_session.await_args.args
    )
    assert str(session_id) == SESSION_ID
    assert user_id == USER_ID
    assert payload.energy_before == 9


def test_finish_session_uses_current_user_id() -> None:
    client = make_client()
    training_session_service.finish_training_session = AsyncMock(
        return_value=make_training_session(
            status="COMPLETED",
            finished_at=datetime.now(UTC),
            notes_after="Treino forte e consistente.",
        )
    )

    response = client.post(
        f"/sessions/{SESSION_ID}/finish",
        json={"notes_after": "Treino forte e consistente."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"
    _, session_id, user_id, payload = (
        training_session_service.finish_training_session.await_args.args
    )
    assert str(session_id) == SESSION_ID
    assert user_id == USER_ID
    assert payload.notes_after == "Treino forte e consistente."


def test_cancel_session_uses_current_user_id() -> None:
    client = make_client()
    training_session_service.cancel_training_session = AsyncMock(
        return_value=make_training_session(status="CANCELLED")
    )

    response = client.post(f"/sessions/{SESSION_ID}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    _, session_id, user_id = training_session_service.cancel_training_session.await_args.args
    assert str(session_id) == SESSION_ID
    assert user_id == USER_ID


async def test_update_training_session_rejects_closed_session() -> None:
    training_session_repository = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=make_training_session(status="COMPLETED")),
        update=AsyncMock(),
    )
    service = TrainingSessionService(
        training_session_repository=training_session_repository,
        profile_repository=SimpleNamespace(),
        skill_repository=SimpleNamespace(),
    )
    payload = TrainingSessionUpdate(energy_before=8)

    try:
        await service.update_training_session(make_db_session(), SESSION_ID, USER_ID, payload)
    except TrainingSessionClosedError:
        pass
    else:
        raise AssertionError("Expected closed session to be rejected")

    training_session_repository.update.assert_not_called()


async def test_finish_training_session_rejects_closed_session() -> None:
    training_session_repository = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=make_training_session(status="CANCELLED")),
        finish=AsyncMock(),
    )
    service = TrainingSessionService(
        training_session_repository=training_session_repository,
        profile_repository=SimpleNamespace(),
        skill_repository=SimpleNamespace(),
    )
    payload = TrainingSessionFinish(notes_after="late finish")

    try:
        await service.finish_training_session(make_db_session(), SESSION_ID, USER_ID, payload)
    except TrainingSessionClosedError:
        pass
    else:
        raise AssertionError("Expected closed session to be rejected")

    training_session_repository.finish.assert_not_called()


async def test_cancel_training_session_rejects_closed_session() -> None:
    training_session_repository = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=make_training_session(status="COMPLETED")),
        cancel=AsyncMock(),
    )
    service = TrainingSessionService(
        training_session_repository=training_session_repository,
        profile_repository=SimpleNamespace(),
        skill_repository=SimpleNamespace(),
    )

    try:
        await service.cancel_training_session(make_db_session(), SESSION_ID, USER_ID)
    except TrainingSessionClosedError:
        pass
    else:
        raise AssertionError("Expected closed session to be rejected")

    training_session_repository.cancel.assert_not_called()


async def test_finish_training_session_rejects_finished_at_before_started_at() -> None:
    started_at = datetime(2026, 7, 16, 18, 0, tzinfo=UTC)
    training_session_repository = SimpleNamespace(
        get_by_id_and_user=AsyncMock(
            return_value=make_training_session(started_at=started_at),
        ),
        finish=AsyncMock(),
    )
    service = TrainingSessionService(
        training_session_repository=training_session_repository,
        profile_repository=SimpleNamespace(),
        skill_repository=SimpleNamespace(),
    )
    payload = TrainingSessionFinish(
        finished_at=datetime(2026, 7, 16, 17, 59, tzinfo=UTC),
        notes_after="invalid finish",
    )

    try:
        await service.finish_training_session(make_db_session(), SESSION_ID, USER_ID, payload)
    except TrainingSessionInvalidFinishError:
        pass
    else:
        raise AssertionError("Expected invalid finish to be rejected")

    training_session_repository.finish.assert_not_called()
