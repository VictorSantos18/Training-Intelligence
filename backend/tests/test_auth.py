from unittest.mock import Mock, patch

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.main import create_app


def test_me_requires_bearer_token() -> None:
    client = TestClient(create_app())

    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing bearer token"}


def test_me_rejects_invalid_bearer_token() -> None:
    client = TestClient(create_app())

    response = client.get("/me", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid bearer token"}


def test_me_returns_current_user_from_valid_token() -> None:
    claims = {
        "sub": "user-123",
        "email": "person@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "https://example.supabase.co/auth/v1",
        "exp": 4_102_444_800,
    }
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    token = jwt.encode(claims, private_key, algorithm="ES256", headers={"kid": "test-key"})
    signing_key = Mock(key=public_key)

    with (
        patch("app.core.auth._require_supabase_auth_settings") as auth_settings,
        patch("app.core.auth.get_jwk_client") as jwk_client,
    ):
        auth_settings.return_value = (
            "https://example.supabase.co/auth/v1/.well-known/jwks.json",
            "https://example.supabase.co/auth/v1",
            "authenticated",
        )
        jwk_client.return_value.get_signing_key_from_jwt.return_value = signing_key

        client = TestClient(create_app())
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "id": "user-123",
        "email": "person@example.com",
        "role": "authenticated",
    }
