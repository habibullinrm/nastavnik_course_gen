"""
Роутер для логирования шагов pipeline.

Endpoints:
- POST /api/logs/step - сохранение лога шага от ML сервиса
- GET /api/logs/track/{track_id} - все логи трека
- GET /api/logs/track/{track_id}/step/{step_name} - лог конкретного шага
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db
from backend.src.models.generation_log import GenerationLog

router = APIRouter(prefix="/api/logs", tags=["logs"])


class StepLogRequest(BaseModel):
    """Запрос на сохранение лога шага."""

    track_id: uuid.UUID
    step_name: str
    step_output: dict
    llm_calls: List[dict] = []
    step_duration_sec: float
    error_message: str | None = None


class StepLogResponse(BaseModel):
    """Ответ с сохранённым логом."""

    id: uuid.UUID
    track_id: uuid.UUID
    step_name: str
    step_output: dict
    llm_calls: List[dict]
    step_duration_sec: float
    error_message: str | None

    class Config:
        from_attributes = True


@router.post("/step", response_model=StepLogResponse, status_code=status.HTTP_201_CREATED)
async def create_step_log(
    log_request: StepLogRequest,
    db: AsyncSession = Depends(get_db),
) -> StepLogResponse:
    """
    Сохраняет лог выполнения шага pipeline.

    Вызывается ML сервисом после каждого шага B1-B8.

    Args:
        log_request: Данные лога шага
        db: Сессия базы данных

    Returns:
        StepLogResponse: Сохранённый лог
    """
    log = GenerationLog(
        track_id=log_request.track_id,
        step_name=log_request.step_name,
        step_output=log_request.step_output,
        llm_calls=log_request.llm_calls,
        step_duration_sec=log_request.step_duration_sec,
        error_message=log_request.error_message,
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return StepLogResponse.model_validate(log)


@router.get("/track/{track_id}", response_model=List[StepLogResponse])
async def get_track_logs(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[StepLogResponse]:
    """
    Получает все логи трека (B1-B8).

    Args:
        track_id: UUID трека
        db: Сессия базы данных

    Returns:
        List[StepLogResponse]: Список логов по порядку
    """
    result = await db.execute(
        select(GenerationLog)
        .where(GenerationLog.track_id == track_id)
        .order_by(GenerationLog.created_at)
    )
    logs = result.scalars().all()

    return [StepLogResponse.model_validate(log) for log in logs]


@router.get("/track/{track_id}/step/{step_name}", response_model=StepLogResponse)
async def get_step_log(
    track_id: uuid.UUID,
    step_name: str,
    db: AsyncSession = Depends(get_db),
) -> StepLogResponse:
    """
    Получает лог конкретного шага трека.

    Args:
        track_id: UUID трека
        step_name: Название шага (B1, B2, ..., B8)
        db: Сессия базы данных

    Returns:
        StepLogResponse: Лог шага

    Raises:
        HTTPException: 404 если лог не найден
    """
    result = await db.execute(
        select(GenerationLog)
        .where(
            GenerationLog.track_id == track_id,
            GenerationLog.step_name == step_name,
        )
        .order_by(GenerationLog.created_at.desc())
        .limit(1)
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log for track {track_id}, step {step_name} not found",
        )

    return StepLogResponse.model_validate(log)
