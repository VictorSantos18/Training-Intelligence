from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.main import create_app
from app.modules.body_regions.router import body_region_service

USER_ID = "5f6a2fb7-2ebd-455d-a118-69d55d01c08d"
BODY_REGION_ID = "278e2f4d-f2fb-43c4-9407-bcde83a06834"


def make_body_region(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    values = {
        "id": BODY_REGION_ID,
        "code": "left_shoulder",
        "name": "Ombro esquerdo",
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


def test_list_body_regions_returns_catalog() -> None:
    client = make_client()
    body_region_service.list_body_regions = AsyncMock(return_value=[make_body_region()])

    response = client.get("/body-regions")

    assert response.status_code == 200
    assert response.json()[0]["id"] == BODY_REGION_ID
    assert response.json()[0]["code"] == "left_shoulder"
    body_region_service.list_body_regions.assert_awaited_once()
