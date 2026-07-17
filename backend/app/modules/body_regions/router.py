from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.body_regions.schemas import BodyRegionRead
from app.modules.body_regions.service import BodyRegionService

router = APIRouter(tags=["body-regions"])
body_region_service = BodyRegionService()


@router.get("/body-regions", response_model=list[BodyRegionRead])
async def list_body_regions(
    _current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[BodyRegionRead]:
    return await body_region_service.list_body_regions(session)
