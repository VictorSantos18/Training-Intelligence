from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.pain_records.exceptions import (
    PainRecordContextMismatchError,
    PainRecordNotFoundError,
    PainRecordTrainingSessionNotFoundError,
    PainRecordTrainingSetNotFoundError,
    PainRecordTrainingSetRequiredError,
)
from app.modules.pain_records.schemas import PainRecordCreate, PainRecordRead, PainRecordUpdate
from app.modules.pain_records.service import PainRecordService

router = APIRouter(tags=["pain-records"])
pain_record_service = PainRecordService()


@router.get("/pain-records", response_model=list[PainRecordRead])
async def list_pain_records(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    training_session_id: Annotated[UUID | None, Query()] = None,
    training_set_id: Annotated[UUID | None, Query()] = None,
) -> list[PainRecordRead]:
    return await pain_record_service.list_pain_records(
        session,
        current_user.id,
        training_session_id,
        training_set_id,
    )


@router.post(
    "/pain-records",
    response_model=PainRecordRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_pain_record(
    payload: PainRecordCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PainRecordRead:
    try:
        return await pain_record_service.create_pain_record(session, current_user.id, payload)
    except PainRecordTrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc
    except PainRecordTrainingSetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training set not found",
        ) from exc
    except PainRecordContextMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training set does not belong to the informed training session",
        ) from exc


@router.get("/pain-records/{pain_record_id}", response_model=PainRecordRead)
async def get_pain_record(
    pain_record_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PainRecordRead:
    try:
        return await pain_record_service.get_pain_record(
            session,
            pain_record_id,
            current_user.id,
        )
    except PainRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pain record not found",
        ) from exc


@router.patch("/pain-records/{pain_record_id}", response_model=PainRecordRead)
async def update_pain_record(
    pain_record_id: UUID,
    payload: PainRecordUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PainRecordRead:
    try:
        return await pain_record_service.update_pain_record(
            session,
            pain_record_id,
            current_user.id,
            payload,
        )
    except PainRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pain record not found",
        ) from exc
    except PainRecordTrainingSetRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="DURING_SET pain records require training_set_id",
        ) from exc


@router.delete("/pain-records/{pain_record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pain_record(
    pain_record_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    try:
        await pain_record_service.delete_pain_record(session, pain_record_id, current_user.id)
    except PainRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pain record not found",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
