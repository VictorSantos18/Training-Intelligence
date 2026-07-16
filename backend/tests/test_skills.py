from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.skills.router import skill_service


def make_skill(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": "2cc2e4e3-e961-46ff-9679-156c79ffed69",
        "name": "Front Lever",
        "description": "Static pull skill",
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


async def override_current_user() -> CurrentUser:
    return CurrentUser(
        id="5f6a2fb7-2ebd-455d-a118-69d55d01c08d",
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


def test_create_skill_rejects_user_id_from_body() -> None:
    client = make_client()

    response = client.post(
        "/skills",
        json={
            "name": "Front Lever",
            "user_id": "b5a01308-78ea-477a-9205-5e010e5d37c7",
        },
    )

    assert response.status_code == 422


def test_create_skill_uses_current_user_id() -> None:
    client = make_client()
    skill_service.create_skill = AsyncMock(return_value=make_skill())

    response = client.post("/skills", json={"name": "Front Lever"})

    assert response.status_code == 201
    assert response.json()["name"] == "Front Lever"
    _, user_id, payload = skill_service.create_skill.await_args.args
    assert user_id == "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
    assert payload.name == "Front Lever"


def test_list_skills_uses_current_user_id() -> None:
    client = make_client()
    skill_service.list_skills = AsyncMock(return_value=[make_skill()])

    response = client.get("/skills")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Front Lever"
    _, user_id = skill_service.list_skills.await_args.args
    assert user_id == "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"


def test_get_skill_uses_current_user_id() -> None:
    client = make_client()
    skill_service.get_skill = AsyncMock(return_value=make_skill())

    response = client.get("/skills/2cc2e4e3-e961-46ff-9679-156c79ffed69")

    assert response.status_code == 200
    _, skill_id, user_id = skill_service.get_skill.await_args.args
    assert str(skill_id) == "2cc2e4e3-e961-46ff-9679-156c79ffed69"
    assert user_id == "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"


def test_update_skill_uses_current_user_id() -> None:
    client = make_client()
    skill_service.update_skill = AsyncMock(return_value=make_skill(status="PAUSED"))

    response = client.patch(
        "/skills/2cc2e4e3-e961-46ff-9679-156c79ffed69",
        json={"status": "PAUSED"},
    )

    assert response.status_code == 200
    _, skill_id, user_id, payload = skill_service.update_skill.await_args.args
    assert str(skill_id) == "2cc2e4e3-e961-46ff-9679-156c79ffed69"
    assert user_id == "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
    assert payload.status == "PAUSED"


def test_delete_skill_uses_current_user_id() -> None:
    client = make_client()
    skill_service.delete_skill = AsyncMock(return_value=None)

    response = client.delete("/skills/2cc2e4e3-e961-46ff-9679-156c79ffed69")

    assert response.status_code == 204
    _, skill_id, user_id = skill_service.delete_skill.await_args.args
    assert str(skill_id) == "2cc2e4e3-e961-46ff-9679-156c79ffed69"
    assert user_id == "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
