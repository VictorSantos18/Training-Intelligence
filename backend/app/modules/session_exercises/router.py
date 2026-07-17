from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.session_exercises.exceptions import (
    SessionExerciseExerciseNotFoundError,
    SessionExerciseNotFoundError,
    SessionExerciseOrderAlreadyExistsError,
    SessionExerciseSkillMismatchError,
    SessionExerciseTrainingSessionClosedError,
    SessionExerciseTrainingSessionNotFoundError,
)
from app.modules.session_exercises.schemas import (
    SessionExerciseCreate,
    SessionExerciseRead,
    SessionExerciseUpdate,
)
from app.modules.session_exercises.service import SessionExerciseService

router = APIRouter(tags=["session-exercises"])
session_exercise_service = SessionExerciseService()


@router.get(
    "/sessions/{session_id}/exercises",
    response_model=list[SessionExerciseRead],
)
async def list_session_exercises(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[SessionExerciseRead]:
    try:
        return await session_exercise_service.list_session_exercises(
            session,
            session_id,
            current_user.id,
        )
    except SessionExerciseTrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc


@router.post(
    "/sessions/{session_id}/exercises",
    response_model=SessionExerciseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_session_exercise(
    session_id: UUID,
    payload: SessionExerciseCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionExerciseRead:
    try:
        return await session_exercise_service.create_session_exercise(
            session,
            session_id,
            current_user.id,
            payload,
        )
    except SessionExerciseTrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc
    except SessionExerciseExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        ) from exc
    except SessionExerciseTrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
    except SessionExerciseSkillMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Exercise does not belong to the training session skill",
        ) from exc
    except SessionExerciseOrderAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execution order already exists in this training session",
        ) from exc


@router.patch("/session-exercises/{session_exercise_id}", response_model=SessionExerciseRead)
async def update_session_exercise(
    session_exercise_id: UUID,
    payload: SessionExerciseUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionExerciseRead:
    try:
        return await session_exercise_service.update_session_exercise(
            session,
            session_exercise_id,
            current_user.id,
            payload,
        )
    except SessionExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session exercise not found",
        ) from exc
    except SessionExerciseTrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
    except SessionExerciseOrderAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execution order already exists in this training session",
        ) from exc


@router.delete(
    "/session-exercises/{session_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session_exercise(
    session_exercise_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    try:
        await session_exercise_service.delete_session_exercise(
            session,
            session_exercise_id,
            current_user.id,
        )
    except SessionExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session exercise not found",
        ) from exc
    except SessionExerciseTrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
