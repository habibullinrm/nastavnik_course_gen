"""
Сервис для управления персонализированными треками.

Предоставляет функции:
- generate_track: Запуск генерации трека через ML pipeline
- get_track: Получение трека по ID
- list_tracks: Список всех треков с фильтрами
"""

import uuid
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.config import settings
from backend.src.models.personalized_track import PersonalizedTrack
from backend.src.schemas.track import (
    GenerationStartedResponse,
    TrackDetail,
    TrackSummary,
    TrackListResponse,
)


async def generate_track(
    profile_id: uuid.UUID,
    db: AsyncSession,
) -> GenerationStartedResponse:
    """
    Запускает генерацию персонализированного трека через ML pipeline.

    Args:
        profile_id: UUID профиля студента
        db: Сессия базы данных

    Returns:
        GenerationStartedResponse: ID трека и URL прогресса

    Raises:
        HTTPException: Если профиль не найден или ML сервис недоступен
    """
    from backend.src.models.student_profile import StudentProfile

    # Получить профиль
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

    # Создать запись трека со статусом "pending"
    track = PersonalizedTrack(
        id=uuid.uuid4(),
        profile_id=profile_id,
        track_data={},
        generation_metadata={},
        algorithm_version="v1.0",
        status="pending",
    )
    db.add(track)
    await db.commit()
    await db.refresh(track)

    # Запустить генерацию асинхронно через ML сервис
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/pipeline/run",
                json={"profile": profile.data},
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            # Обновить трек результатом
            track.track_data = result_data.get("track_data", {})
            track.generation_metadata = result_data.get("metadata", {})
            track.generation_duration_sec = result_data.get("metadata", {}).get("total_duration_sec", 0)
            track.status = "completed"
            track.updated_at = datetime.utcnow()
            
            await db.commit()
            
        except httpx.HTTPError as e:
            # Обновить статус на failed
            track.status = "failed"
            track.error_message = str(e)
            track.updated_at = datetime.utcnow()
            await db.commit()
            raise

    return GenerationStartedResponse(
        track_id=track.id,
        progress_url=f"/api/tracks/{track.id}/progress",
    )


async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession,
) -> Optional[TrackDetail]:
    """
    Получает детальную информацию о треке.

    Args:
        track_id: UUID трека
        db: Сессия базы данных

    Returns:
        TrackDetail или None если не найден
    """
    result = await db.execute(
        select(PersonalizedTrack).where(PersonalizedTrack.id == track_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        return None

    return TrackDetail(
        id=track.id,
        profile_id=track.profile_id,
        track_data=track.track_data,
        generation_metadata=track.generation_metadata,
        algorithm_version=track.algorithm_version,
        validation_b8=track.validation_b8 or {},
        status=track.status,
        error_message=track.error_message,
        generation_duration_sec=track.generation_duration_sec,
        created_at=track.created_at,
        updated_at=track.updated_at,
    )


async def list_tracks(
    db: AsyncSession,
    profile_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> TrackListResponse:
    """
    Получает список треков с фильтрацией.

    Args:
        db: Сессия базы данных
        profile_id: Фильтр по профилю (опционально)
        status: Фильтр по статусу (опционально)
        limit: Максимальное количество результатов
        offset: Смещение для пагинации

    Returns:
        TrackListResponse: Список треков с метаданными
    """
    query = select(PersonalizedTrack)

    if profile_id:
        query = query.where(PersonalizedTrack.profile_id == profile_id)
    if status:
        query = query.where(PersonalizedTrack.status == status)

    query = query.order_by(PersonalizedTrack.created_at.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    tracks = result.scalars().all()

    # Подсчёт общего количества
    count_query = select(PersonalizedTrack)
    if profile_id:
        count_query = count_query.where(PersonalizedTrack.profile_id == profile_id)
    if status:
        count_query = count_query.where(PersonalizedTrack.status == status)

    from sqlalchemy import func
    count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
    total = count_result.scalar() or 0

    items = [
        TrackSummary(
            id=track.id,
            profile_id=track.profile_id,
            status=track.status,
            algorithm_version=track.algorithm_version,
            generation_duration_sec=track.generation_duration_sec,
            created_at=track.created_at,
        )
        for track in tracks
    ]

    return TrackListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
