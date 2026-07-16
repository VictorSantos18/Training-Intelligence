from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.modules.sessions.exceptions import (
    TrainingSessionClosedError,
    TrainingSessionInvalidFinishError,
    TrainingSessionNotFoundError,
    TrainingSessionSkillNotFoundError,
)
from app.modules.sessions.schemas import (
    TrainingSessionCreate,
    TrainingSessionFinish,
    TrainingSessionRead,
    TrainingSessionStatus,
    TrainingSessionUpdate,
)
from app.modules.sessions.service import TrainingSessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])
training_session_service = TrainingSessionService()


@router.get("", response_model=list[TrainingSessionRead])
async def list_training_sessions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skill_id: Annotated[UUID | None, Query()] = None,
    status_filter: Annotated[TrainingSessionStatus | None, Query(alias="status")] = None,
) -> list[TrainingSessionRead]:
    return await training_session_service.list_training_sessions(
        session,
        current_user.id,
        skill_id=skill_id,
        status=status_filter,
    )


@router.post("", response_model=TrainingSessionRead, status_code=status.HTTP_201_CREATED)
async def create_training_session(
    payload: TrainingSessionCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSessionRead:
    try:
        return await training_session_service.create_training_session(
            session,
            current_user.id,
            payload,
        )
    except TrainingSessionSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        ) from exc


@router.get("/{session_id}", response_model=TrainingSessionRead)
async def get_training_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSessionRead:
    try:
        return await training_session_service.get_training_session(
            session,
            session_id,
            current_user.id,
        )
    except TrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc


@router.patch("/{session_id}", response_model=TrainingSessionRead)
async def update_training_session(
    session_id: UUID,
    payload: TrainingSessionUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSessionRead:
    try:
        return await training_session_service.update_training_session(
            session,
            session_id,
            current_user.id,
            payload,
        )
    except TrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc
    except TrainingSessionSkillNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        ) from exc
    except TrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc


@router.post("/{session_id}/finish", response_model=TrainingSessionRead)
async def finish_training_session(
    session_id: UUID,
    payload: TrainingSessionFinish,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSessionRead:
    try:
        return await training_session_service.finish_training_session(
            session,
            session_id,
            current_user.id,
            payload,
        )
    except TrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc
    except TrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
    except TrainingSessionInvalidFinishError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="finished_at must be after started_at",
        ) from exc


@router.post("/{session_id}/cancel", response_model=TrainingSessionRead)
async def cancel_training_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TrainingSessionRead:
    try:
        return await training_session_service.cancel_training_session(
            session,
            session_id,
            current_user.id,
        )
    except TrainingSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        ) from exc
    except TrainingSessionClosedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Training session is already closed",
        ) from exc
