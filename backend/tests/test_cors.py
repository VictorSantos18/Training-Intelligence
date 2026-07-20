from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

VERCEL_ORIGIN = "https://training-intelligence-lyart.vercel.app"
LOCALHOST_ORIGIN = "http://localhost:3000"
LOOPBACK_ORIGIN = "http://127.0.0.1:3000"
UNKNOWN_ORIGIN = "https://unknown.example.com"


def make_client() -> TestClient:
    settings = Settings(
        _env_file=None,
        environment="development",
        database_url="postgresql+asyncpg://training:training@localhost:5433/training",
        frontend_url=LOCALHOST_ORIGIN,
        cors_origins=f"{LOCALHOST_ORIGIN},{LOOPBACK_ORIGIN},{VERCEL_ORIGIN}",
    )
    return TestClient(create_app(settings))


def test_cors_allows_vercel_origin() -> None:
    client = make_client()

    response = client.get("/health", headers={"Origin": VERCEL_ORIGIN})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN


def test_cors_allows_localhost_origin() -> None:
    client = make_client()

    response = client.get("/health", headers={"Origin": LOCALHOST_ORIGIN})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == LOCALHOST_ORIGIN


def test_cors_does_not_allow_unknown_origin() -> None:
    client = make_client()

    response = client.get("/health", headers={"Origin": UNKNOWN_ORIGIN})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_options_allows_vercel_origin() -> None:
    client = make_client()

    response = client.options(
        "/analytics/overview",
        headers={
            "Origin": VERCEL_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == VERCEL_ORIGIN
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
