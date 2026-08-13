from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.analytics.exceptions import (
    AnalysisReportEmptyPeriodError,
    AnalysisReportNotFoundError,
    AnalysisReportSkillNotFoundError,
)
from app.modules.analytics.schemas import (
    AnalysisReportGenerate,
    AnalysisReportListItem,
    AnalysisReportRead,
    AnalysisReportUpdate,
    AnalyticsOverview,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalyticsOverview:
    return await analytics_service.get_overview(session, current_user.id)


@router.get("/reports", response_model=list[AnalysisReportListItem])
async def list_analysis_reports(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[AnalysisReportListItem]:
    return await analytics_service.list_reports(session, current_user.id, limit)


@router.post(
    "/reports",
    response_model=AnalysisReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_analysis_report(
    payload: AnalysisReportGenerate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalysisReportRead:
    try:
        return await analytics_service.generate_report(session, current_user.id, payload)
    except AnalysisReportSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        ) from exc
    except AnalysisReportEmptyPeriodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No completed sessions found for this period",
        ) from exc


@router.get("/reports/{report_id}", response_model=AnalysisReportRead)
async def get_analysis_report(
    report_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalysisReportRead:
    try:
        return await analytics_service.get_report(session, report_id, current_user.id)
    except AnalysisReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis report not found",
        ) from exc


@router.patch("/reports/{report_id}", response_model=AnalysisReportRead)
async def update_analysis_report(
    report_id: UUID,
    payload: AnalysisReportUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalysisReportRead:
    try:
        return await analytics_service.update_report(session, report_id, current_user.id, payload)
    except AnalysisReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis report not found",
        ) from exc
