"""
Роутер для управления персонализированными треками.

Endpoints:
- POST /api/tracks/generate - запуск генерации трека
- GET /api/tracks/{id} - получение трека по ID
- GET /api/tracks/{id}/progress - SSE прогресс генерации
- GET /api/tracks - список треков с фильтрами
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db
from backend.src.schemas.track import (
    GenerationStartedResponse,
    TrackDetail,
    TrackListResponse,
)
from backend.src.services import track_service

router = APIRouter(prefix="/api/tracks", tags=["tracks"])


@router.post("/generate", response_model=GenerationStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_track(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GenerationStartedResponse:
    """
    Запускает генерацию персонализированного трека.

    Args:
        profile_id: UUID профиля студента
        db: Сессия базы данных

    Returns:
        GenerationStartedResponse: ID трека и URL прогресса

    Raises:
        HTTPException: 404 если профиль не найден, 500 если ML сервис недоступен
    """
    try:
        result = await track_service.generate_track(profile_id, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )


@router.get("/{track_id}", response_model=TrackDetail)
async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TrackDetail:
    """
    Получает детальную информацию о треке.

    Args:
        track_id: UUID трека
        db: Сессия базы данных

    Returns:
        TrackDetail: Детальная информация о треке

    Raises:
        HTTPException: 404 если трек не найден
    """
    track = await track_service.get_track(track_id, db)

    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found",
        )

    return track


@router.get("/{track_id}/progress")
async def get_track_progress(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    SSE endpoint для получения прогресса генерации трека.

    Args:
        track_id: UUID трека
        db: Сессия базы данных

    Returns:
        StreamingResponse: SSE stream с прогрессом

    Note:
        В текущей реализации возвращает финальный статус.
        Для real-time прогресса нужно проксировать ML /pipeline/run-stream.
    """
    import json
    
    async def event_generator():
        track = await track_service.get_track(track_id, db)
        if not track:
            yield f"data: {json.dumps({'error': 'Track not found'})}\n\n"
            return
        
        yield f"data: {json.dumps({'status': track.status, 'track_id': str(track.id)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.get("/", response_model=TrackListResponse)
async def list_tracks(
    profile_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> TrackListResponse:
    """
    Получает список треков с фильтрацией и пагинацией.

    Args:
        profile_id: Фильтр по профилю (опционально)
        status: Фильтр по статусу (опционально)
        limit: Максимальное количество результатов
        offset: Смещение для пагинации
        db: Сессия базы данных

    Returns:
        TrackListResponse: Список треков с метаданными
    """
    return await track_service.list_tracks(
        db=db,
        profile_id=profile_id,
        status=status,
        limit=limit,
        offset=offset,
    )
