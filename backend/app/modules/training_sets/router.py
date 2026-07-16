from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.training_sets.exceptions import (
    TrainingSetNotFoundError,
    TrainingSetNumberAlreadyExistsError,
    TrainingSetSessionClosedError,
    TrainingSetSessionExerciseNotFoundError,
)
from app.modules.training_sets.schemas import TrainingSetCreate, TrainingSetRead, TrainingSetUpdate
from app.modules.training_sets.service import TrainingSetService

router = APIRouter(tags=["training-sets"])
training_set_service = TrainingSetService()


@router.post(
    "/session-exercises/{session_exercise_id}/sets",
    response_model=TrainingSetRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_training_set(
    session_exercise_id: UUID,
    payload: TrainingSetCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSetRead:
    try:
        return await training_set_service.create_training_set(
            session,
            session_exercise_id,
            current_user.id,
            payload,
        )
    except TrainingSetSessionExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session exercise not found",
        ) from exc
    except TrainingSetSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
    except TrainingSetNumberAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Set number already exists in this session exercise",
        ) from exc


@router.patch("/sets/{set_id}", response_model=TrainingSetRead)
async def update_training_set(
    set_id: UUID,
    payload: TrainingSetUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSetRead:
    try:
        return await training_set_service.update_training_set(
            session,
            set_id,
            current_user.id,
            payload,
        )
    except TrainingSetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training set not found",
        ) from exc
    except TrainingSetSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
    except TrainingSetNumberAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Set number already exists in this session exercise",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_set(
    set_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    try:
        await training_set_service.delete_training_set(session, set_id, current_user.id)
    except TrainingSetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training set not found",
        ) from exc
    except TrainingSetSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)

