from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
async def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str | None]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }
