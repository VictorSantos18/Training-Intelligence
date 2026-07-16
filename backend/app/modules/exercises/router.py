from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.exercises.exceptions import (
    ExerciseNameAlreadyExistsError,
    ExerciseNotFoundError,
    ExerciseSkillNotFoundError,
)
from app.modules.exercises.schemas import ExerciseCreate, ExerciseRead, ExerciseUpdate
from app.modules.exercises.service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["exercises"])
exercise_service = ExerciseService()


@router.get("", response_model=list[ExerciseRead])
async def list_exercises(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skill_id: Annotated[UUID | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
) -> list[ExerciseRead]:
    return await exercise_service.list_exercises(
        session,
        current_user.id,
        skill_id=skill_id,
        is_active=is_active,
    )


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    payload: ExerciseCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExerciseRead:
    try:
        return await exercise_service.create_exercise(session, current_user.id, payload)
    except ExerciseSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        ) from exc
    except ExerciseNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise name already exists",
        ) from exc


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExerciseRead:
    try:
        return await exercise_service.get_exercise(session, exercise_id, current_user.id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        ) from exc


@router.patch("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: UUID,
    payload: ExerciseUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExerciseRead:
    try:
        return await exercise_service.update_exercise(
            session,
            exercise_id,
            current_user.id,
            payload,
        )
    except ExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        ) from exc
    except ExerciseSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        ) from exc
    except ExerciseNameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise name already exists",
        ) from exc


@router.delete("/{exercise_id}", response_model=ExerciseRead)
async def delete_exercise(
    exercise_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExerciseRead:
    try:
        return await exercise_service.deactivate_exercise(session, exercise_id, current_user.id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        ) from exc

