from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.pain_records.router import pain_record_service

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
TRAINING_SESSION_ID = "3f527bd7-5b7e-40d9-931f-ff176c6499df"
TRAINING_SET_ID = "01ce428b-ae51-42ce-ad8f-b6e57ba73da2"
BODY_REGION_ID = "278e2f4d-f2fb-43c4-9407-bcde83a06834"
PAIN_RECORD_ID = "9b0da4fa-e5d6-4634-8046-3d8093f4754b"


def make_pain_record(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": PAIN_RECORD_ID,
        "user_id": USER_ID,
        "training_session_id": TRAINING_SESSION_ID,
        "training_set_id": None,
        "body_region_id": BODY_REGION_ID,
        "occurred_at": now,
        "side": "LEFT",
        "moment": "POST_SESSION",
        "intensity": 3,
        "description": "Mild discomfort",
        "notes": None,
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


def test_create_pain_record_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        "/pain-records",
        json={
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
            "training_session_id": TRAINING_SESSION_ID,
            "body_region_id": BODY_REGION_ID,
            "side": "LEFT",
            "moment": "POST_SESSION",
            "intensity": 3,
        },
    )

    assert response.status_code == 422


def test_create_pain_record_uses_current_user_id() -> None:
    client = make_client()
    pain_record_service.create_pain_record = AsyncMock(return_value=make_pain_record())

    response = client.post(
        "/pain-records",
        json={
            "training_session_id": TRAINING_SESSION_ID,
            "body_region_id": BODY_REGION_ID,
            "side": "LEFT",
            "moment": "POST_SESSION",
            "intensity": 3,
            "description": "Mild discomfort",
        },
    )

    assert response.status_code == 201
    assert response.json()["body_region_id"] == BODY_REGION_ID
    _, user_id, payload = pain_record_service.create_pain_record.await_args.args
    assert user_id == USER_ID
    assert str(payload.training_session_id) == TRAINING_SESSION_ID
    assert str(payload.body_region_id) == BODY_REGION_ID


def test_create_pain_record_requires_training_context() -> None:
    client = make_client()

    response = client.post(
        "/pain-records",
        json={
            "body_region_id": BODY_REGION_ID,
            "side": "LEFT",
            "moment": "POST_SESSION",
            "intensity": 3,
        },
    )

    assert response.status_code == 422


def test_create_pain_record_requires_training_set_for_during_set_moment() -> None:
    client = make_client()

    response = client.post(
        "/pain-records",
        json={
            "training_session_id": TRAINING_SESSION_ID,
            "body_region_id": BODY_REGION_ID,
            "side": "LEFT",
            "moment": "DURING_SET",
            "intensity": 3,
        },
    )

    assert response.status_code == 422


def test_list_pain_records_uses_current_user_id() -> None:
    client = make_client()
    pain_record_service.list_pain_records = AsyncMock(return_value=[make_pain_record()])

    response = client.get(f"/pain-records?training_session_id={TRAINING_SESSION_ID}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    _, user_id, training_session_id, training_set_id = (
        pain_record_service.list_pain_records.await_args.args
    )
    assert user_id == USER_ID
    assert str(training_session_id) == TRAINING_SESSION_ID
    assert training_set_id is None


def test_get_pain_record_uses_current_user_id() -> None:
    client = make_client()
    pain_record_service.get_pain_record = AsyncMock(return_value=make_pain_record())

    response = client.get(f"/pain-records/{PAIN_RECORD_ID}")

    assert response.status_code == 200
    _, pain_record_id, user_id = pain_record_service.get_pain_record.await_args.args
    assert str(pain_record_id) == PAIN_RECORD_ID
    assert user_id == USER_ID


def test_update_pain_record_uses_current_user_id() -> None:
    client = make_client()
    pain_record_service.update_pain_record = AsyncMock(
        return_value=make_pain_record(intensity=4)
    )

    response = client.patch(f"/pain-records/{PAIN_RECORD_ID}", json={"intensity": 4})

    assert response.status_code == 200
    assert response.json()["intensity"] == 4
    _, pain_record_id, user_id, payload = pain_record_service.update_pain_record.await_args.args
    assert str(pain_record_id) == PAIN_RECORD_ID
    assert user_id == USER_ID
    assert payload.intensity == 4


def test_delete_pain_record_uses_current_user_id() -> None:
    client = make_client()
    pain_record_service.delete_pain_record = AsyncMock(return_value=None)

    response = client.delete(f"/pain-records/{PAIN_RECORD_ID}")

    assert response.status_code == 204
    _, pain_record_id, user_id = pain_record_service.delete_pain_record.await_args.args
    assert str(pain_record_id) == PAIN_RECORD_ID
    assert user_id == USER_ID
