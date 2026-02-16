"""
Сервис для управления персонализированными треками.

Предоставляет функции:
- generate_track: Запуск генерации трека (background task, 202)
- cancel_track: Остановка генерации (ставит статус cancelling)
- generate_track_batch: Batch-генерация N треков
- get_track / list_tracks: Чтение данных
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.src.core.config import settings
from backend.src.models.personalized_track import PersonalizedTrack
from backend.src.schemas.track import (
    BatchGenerationStartedResponse,
    GenerationStartedResponse,
    TrackDetail,
    TrackSummary,
    TrackListResponse,
)

logger = logging.getLogger(__name__)

# Running background tasks: track_id → asyncio.Task
_running_tasks: dict[uuid.UUID, asyncio.Task] = {}


def _make_session_factory() -> async_sessionmaker[AsyncSession]:
    """Создаёт независимый session factory для background tasks."""
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def _update_track_status(
    session_factory: async_sessionmaker[AsyncSession],
    track_id: uuid.UUID,
    *,
    status: str,
    track_data: dict | None = None,
    generation_metadata: dict | None = None,
    validation_b8: dict | None = None,
    generation_duration_sec: float | None = None,
    error_message: str | None = None,
) -> None:
    """Обновить статус трека в БД (из background task)."""
    async with session_factory() as session:
        values: dict = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }
        if track_data is not None:
            values["track_data"] = track_data
        if generation_metadata is not None:
            values["generation_metadata"] = generation_metadata
        if validation_b8 is not None:
            values["validation_b8"] = validation_b8
        if generation_duration_sec is not None:
            values["generation_duration_sec"] = generation_duration_sec
        if error_message is not None:
            values["error_message"] = error_message

        await session.execute(
            update(PersonalizedTrack)
            .where(PersonalizedTrack.id == track_id)
            .values(**values)
        )
        await session.commit()


async def _run_generation(
    track_id: uuid.UUID,
    profile_data: dict,
    algorithm_version: str,
) -> None:
    """Background task: вызывает ML pipeline и обновляет трек в БД."""
    sf = _make_session_factory()

    # Поставить статус running
    await _update_track_status(sf, track_id, status="running")

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/pipeline/run",
                json={
                    "profile": profile_data,
                    "track_id": str(track_id),
                    "algorithm_version": algorithm_version,
                },
            )
            response.raise_for_status()
            result_data = response.json()

        await _update_track_status(
            sf,
            track_id,
            status="completed",
            track_data=result_data.get("track_data", {}),
            generation_metadata=result_data.get("generation_metadata", {}),
            validation_b8=result_data.get("validation_b8"),
            generation_duration_sec=result_data.get("generation_metadata", {}).get(
                "total_duration_sec", 0
            ),
        )
        logger.info(f"Track {track_id} generation completed")

    except asyncio.CancelledError:
        # Task was cancelled (from cancel_track)
        await _update_track_status(sf, track_id, status="cancelled")
        logger.info(f"Track {track_id} generation cancelled (task.cancel)")

    except httpx.HTTPStatusError as e:
        # ML вернул ошибку — проверяем, может это cancellation
        error_detail = ""
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if "cancelled" in error_detail.lower():
            await _update_track_status(sf, track_id, status="cancelled")
            logger.info(f"Track {track_id} generation cancelled (ML reported)")
        else:
            await _update_track_status(
                sf, track_id, status="failed", error_message=error_detail
            )
            logger.error(f"Track {track_id} generation failed: {error_detail}")

    except Exception as e:
        await _update_track_status(
            sf, track_id, status="failed", error_message=str(e)
        )
        logger.error(f"Track {track_id} generation failed: {e}")

    finally:
        _running_tasks.pop(track_id, None)


async def _run_batch_generation(
    batch_id: uuid.UUID,
    track_ids: list[uuid.UUID],
    profile_data: dict,
    algorithm_version: str,
) -> None:
    """Background task: вызывает ML batch pipeline."""
    sf = _make_session_factory()

    # Поставить статус running для всех треков
    for tid in track_ids:
        await _update_track_status(sf, tid, status="running")

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/pipeline/run-batch",
                json={
                    "profile": profile_data,
                    "track_ids": [str(t) for t in track_ids],
                    "algorithm_version": algorithm_version,
                },
            )
            response.raise_for_status()
            result_data = response.json()

        # result_data.results — массив результатов по каждому треку
        results = result_data.get("results", [])
        for i, res in enumerate(results):
            tid = track_ids[i] if i < len(track_ids) else None
            if not tid:
                continue
            if res.get("status") == "cancelled":
                await _update_track_status(sf, tid, status="cancelled")
            elif res.get("error"):
                await _update_track_status(
                    sf, tid, status="failed", error_message=res["error"]
                )
            else:
                await _update_track_status(
                    sf,
                    tid,
                    status="completed",
                    track_data=res.get("track_data", {}),
                    generation_metadata=res.get("generation_metadata", {}),
                    validation_b8=res.get("validation_b8"),
                    generation_duration_sec=res.get("generation_metadata", {}).get(
                        "total_duration_sec", 0
                    ),
                )

        logger.info(f"Batch {batch_id} generation completed ({len(results)} tracks)")

    except Exception as e:
        # Mark all tracks as failed
        for tid in track_ids:
            await _update_track_status(
                sf, tid, status="failed", error_message=f"Batch error: {e}"
            )
        logger.error(f"Batch {batch_id} generation failed: {e}")

    finally:
        _running_tasks.pop(batch_id, None)


async def generate_track(
    profile_id: uuid.UUID,
    db: AsyncSession,
) -> GenerationStartedResponse:
    """
    Создаёт трек и запускает генерацию в background task.
    Возвращает 202 сразу.
    """
    from backend.src.models.student_profile import StudentProfile

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

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

    # Запустить background task
    task = asyncio.create_task(
        _run_generation(track.id, profile.data, "v1.0")
    )
    _running_tasks[track.id] = task

    return GenerationStartedResponse(
        track_id=track.id,
        status="pending",
        progress_url=f"/api/tracks/{track.id}/progress",
    )


async def generate_track_batch(
    profile_id: uuid.UUID,
    batch_size: int,
    db: AsyncSession,
) -> BatchGenerationStartedResponse:
    """
    Создаёт N треков с общим batch_id и запускает batch pipeline.
    """
    from backend.src.models.student_profile import StudentProfile

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

    batch_id = uuid.uuid4()
    track_ids: list[uuid.UUID] = []

    for i in range(batch_size):
        track = PersonalizedTrack(
            id=uuid.uuid4(),
            profile_id=profile_id,
            track_data={},
            generation_metadata={},
            algorithm_version="v1.0",
            status="pending",
            batch_id=batch_id,
            batch_index=i,
        )
        db.add(track)
        track_ids.append(track.id)

    await db.commit()

    # Запустить background task для batch
    task = asyncio.create_task(
        _run_batch_generation(batch_id, track_ids, profile.data, "v1.0")
    )
    _running_tasks[batch_id] = task

    return BatchGenerationStartedResponse(
        batch_id=batch_id,
        track_ids=track_ids,
        status="pending",
        progress_url=f"/api/tracks/batch/{batch_id}/progress",
    )


async def cancel_track(
    track_id: uuid.UUID,
    db: AsyncSession,
) -> bool:
    """
    Отменяет генерацию трека.
    Ставит статус cancelling — ML проверит между шагами.
    """
    result = await db.execute(
        select(PersonalizedTrack).where(PersonalizedTrack.id == track_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise ValueError(f"Track {track_id} not found")

    if track.status not in ("pending", "running"):
        raise ValueError(f"Cannot cancel track in status '{track.status}'")

    track.status = "cancelling"
    track.updated_at = datetime.utcnow()
    await db.commit()

    # Также отменить asyncio task если он есть
    task = _running_tasks.get(track_id)
    if task and not task.done():
        task.cancel()

    return True


async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession,
) -> Optional[TrackDetail]:
    """Получает детальную информацию о треке."""
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
        batch_id=track.batch_id,
        batch_index=track.batch_index,
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
    """Получает список треков с фильтрацией."""
    query = select(PersonalizedTrack)

    if profile_id:
        query = query.where(PersonalizedTrack.profile_id == profile_id)
    if status:
        query = query.where(PersonalizedTrack.status == status)

    query = query.order_by(PersonalizedTrack.created_at.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    tracks = result.scalars().all()

    from sqlalchemy import func
    count_query = select(PersonalizedTrack)
    if profile_id:
        count_query = count_query.where(PersonalizedTrack.profile_id == profile_id)
    if status:
        count_query = count_query.where(PersonalizedTrack.status == status)

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
        tracks=items,
        total=total,
    )
