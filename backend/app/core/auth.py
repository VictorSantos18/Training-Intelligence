from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None
    role: str | None
    claims: dict


def _raise_auth_error(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _require_supabase_auth_settings() -> tuple[str, str, str]:
    missing = [
        name
        for name, value in {
            "SUPABASE_JWKS_URL": settings.supabase_jwks_url,
            "SUPABASE_JWT_ISSUER": settings.supabase_jwt_issuer,
            "SUPABASE_JWT_AUDIENCE": settings.supabase_jwt_audience,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required auth settings: {', '.join(missing)}")

    return (
        settings.supabase_jwks_url or "",
        settings.supabase_jwt_issuer or "",
        settings.supabase_jwt_audience or "",
    )


@lru_cache
def get_jwk_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> CurrentUser:
    if credentials is None:
        _raise_auth_error("Missing bearer token")

    jwks_url, issuer, audience = _require_supabase_auth_settings()
    token = credentials.credentials

    try:
        signing_key = get_jwk_client(jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "sub"]},
        )
    except (InvalidTokenError, PyJWKClientError):
        _raise_auth_error("Invalid bearer token")

    user_id = claims.get("sub")
    if not isinstance(user_id, str) or not user_id:
        _raise_auth_error("Invalid bearer token")

    email = claims.get("email")
    role = claims.get("role")

    return CurrentUser(
        id=user_id,
        email=email if isinstance(email, str) else None,
        role=role if isinstance(role, str) else None,
        claims=claims,
    )
