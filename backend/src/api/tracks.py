"""
Роутер для управления персонализированными треками.

Endpoints:
- POST /api/tracks/generate - запуск генерации трека (202)
- POST /api/tracks/generate-batch - batch-генерация N треков (202)
- POST /api/tracks/{id}/cancel - остановка генерации
- GET /api/tracks/{id} - получение трека по ID
- GET /api/tracks/{id}/progress - SSE прогресс генерации (polling generation_logs)
- GET /api/tracks/batch/{batch_id}/progress - SSE прогресс batch-генерации
- GET /api/tracks - список треков с фильтрами
"""

import asyncio
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import AsyncSessionLocal, get_db
from backend.src.models.generation_log import GenerationLog
from backend.src.models.personalized_track import PersonalizedTrack
from backend.src.schemas.track import (
    FieldUsageResponse,
    GenerateTrackRequest,
    GenerateBatchRequest,
    GenerationStartedResponse,
    BatchGenerationStartedResponse,
    TrackDetail,
    TrackListResponse,
)
from backend.src.services import field_usage_service, track_service

router = APIRouter(prefix="/api/tracks", tags=["tracks"])

# Описания шагов для SSE events
STEP_DESCRIPTIONS = {
    "B1_validate": "Валидация и обогащение профиля",
    "B2_competencies": "Формулировка компетенций",
    "B3_ksa_matrix": "KSA-матрица (Знания-Умения-Навыки)",
    "B4_learning_units": "Проектирование учебных единиц",
    "B5_hierarchy": "Иерархия и уровни",
    "B6_problem_formulations": "Формулировки проблем (PBL)",
    "B7_schedule": "Сборка расписания",
    "B8_validation": "Валидация трека",
}

# Маппинг step_name → короткое имя (B1..B8)
STEP_SHORT_NAMES = {
    "B1_validate": "B1",
    "B2_competencies": "B2",
    "B3_ksa_matrix": "B3",
    "B4_learning_units": "B4",
    "B5_hierarchy": "B5",
    "B6_problem_formulations": "B6",
    "B7_schedule": "B7",
    "B8_validation": "B8",
}

ALL_STEPS = list(STEP_SHORT_NAMES.keys())


def _step_summary(step_name: str, step_output: dict) -> dict:
    """Извлечь ключевые метрики из step_output для SSE summary."""
    short = STEP_SHORT_NAMES.get(step_name, step_name)
    if short == "B1":
        return {
            "effective_level": step_output.get("effective_level"),
            "estimated_weeks": step_output.get("estimated_weeks"),
        }
    elif short == "B2":
        comps = step_output.get("competencies", [])
        return {"competencies_count": len(comps)}
    elif short == "B3":
        return {
            "knowledge_count": len(step_output.get("knowledge_items", [])),
            "skills_count": len(step_output.get("skill_items", [])),
            "habits_count": len(step_output.get("habit_items", [])),
        }
    elif short == "B4":
        return {
            "units_count": len(step_output.get("units", [])),
            "clusters_count": len(step_output.get("clusters", [])),
        }
    elif short == "B5":
        return {
            "total_weeks": step_output.get("total_weeks"),
            "levels": len(step_output.get("levels", [])),
        }
    elif short == "B6":
        return {
            "blueprints_count": len(step_output.get("blueprints", step_output.get("lesson_blueprints", []))),
        }
    elif short == "B7":
        return {
            "weeks": step_output.get("total_weeks", step_output.get("weeks")),
            "checkpoints": len(step_output.get("checkpoints", [])),
        }
    elif short == "B8":
        return {
            "overall_valid": step_output.get("overall_valid"),
            "checks": len(step_output.get("checks", step_output.get("validation_checks", []))),
        }
    return {}


def _make_sse(event: str, data: dict) -> str:
    """Форматировать SSE event."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/generate", response_model=GenerationStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_track(
    request: GenerateTrackRequest,
    db: AsyncSession = Depends(get_db),
) -> GenerationStartedResponse:
    """Запускает генерацию трека. Возвращает 202 сразу."""
    try:
        result = await track_service.generate_track(request.profile_id, db)
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


@router.post("/generate-batch", response_model=BatchGenerationStartedResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_track_batch(
    request: GenerateBatchRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchGenerationStartedResponse:
    """Запускает batch-генерацию N треков. Возвращает 202 сразу."""
    try:
        result = await track_service.generate_track_batch(
            request.profile_id, request.batch_size, db
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch generation failed: {str(e)}",
        )


@router.post("/{track_id}/cancel")
async def cancel_track(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Останавливает генерацию трека."""
    try:
        await track_service.cancel_track(track_id, db)
        return {"status": "cancelling", "track_id": str(track_id)}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{track_id}/progress")
async def get_track_progress(
    track_id: uuid.UUID,
):
    """
    SSE endpoint для real-time прогресса генерации.
    Поллит generation_logs и статус трека каждые 2 секунды.
    Использует собственные сессии (не DI), т.к. генератор живёт дольше запроса.
    """
    async def event_generator():
        last_seen_step_names: set[str] = set()
        sent_running: set[str] = set()
        timeout_seconds = 600  # 10 минут
        elapsed = 0.0
        poll_interval = 2.0

        # Сначала отправить текущий статус
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PersonalizedTrack).where(PersonalizedTrack.id == track_id)
            )
            track = result.scalar_one_or_none()

        if not track:
            yield _make_sse("error", {"error": "Track not found"})
            return

        # Если трек уже завершён — отдать финальный статус сразу
        if track.status in ("completed", "failed", "cancelled"):
            if track.status == "completed":
                yield _make_sse("complete", {
                    "total_duration_sec": track.generation_duration_sec,
                    "total_tokens": track.generation_metadata.get("total_tokens", 0) if track.generation_metadata else 0,
                })
            elif track.status == "cancelled":
                async with AsyncSessionLocal() as db:
                    log_result = await db.execute(
                        select(GenerationLog)
                        .where(GenerationLog.track_id == track_id)
                        .order_by(GenerationLog.created_at)
                    )
                    logs = log_result.scalars().all()
                completed_steps = [STEP_SHORT_NAMES.get(l.step_name, l.step_name) for l in logs]
                yield _make_sse("cancelled", {
                    "completed_steps": completed_steps,
                    "last_step": completed_steps[-1] if completed_steps else None,
                })
            else:
                yield _make_sse("error", {
                    "error": track.error_message or "Generation failed",
                    "failed_step": None,
                })
            return

        while elapsed < timeout_seconds:
            async with AsyncSessionLocal() as db:
                # Получить новые логи
                result = await db.execute(
                    select(GenerationLog)
                    .where(GenerationLog.track_id == track_id)
                    .order_by(GenerationLog.created_at)
                )
                logs = result.scalars().all()

                completed_step_names = {log.step_name for log in logs}

                # Отправить step_update для новых завершённых шагов
                for log in logs:
                    if log.step_name not in last_seen_step_names:
                        last_seen_step_names.add(log.step_name)
                        short = STEP_SHORT_NAMES.get(log.step_name, log.step_name)

                        tokens_used = 0
                        if log.llm_calls:
                            for call in log.llm_calls:
                                tokens_used += call.get("tokens_used", 0)

                        summary = _step_summary(log.step_name, log.step_output or {})

                        yield _make_sse("step_update", {
                            "step": short,
                            "status": "completed",
                            "description": STEP_DESCRIPTIONS.get(log.step_name, log.step_name),
                            "duration_sec": log.step_duration_sec,
                            "tokens_used": tokens_used,
                            "summary": summary,
                        })

                # Определить следующий шаг (running) — только один одновременно
                next_running = None
                for step_name in ALL_STEPS:
                    if step_name not in completed_step_names:
                        next_running = step_name
                        break

                if next_running and next_running not in sent_running:
                    # Сначала сбросить предыдущий running (если был и теперь завершён)
                    sent_running = {next_running}
                    short = STEP_SHORT_NAMES.get(next_running, next_running)
                    yield _make_sse("step_update", {
                        "step": short,
                        "status": "running",
                        "description": STEP_DESCRIPTIONS.get(next_running, next_running),
                    })

                # Проверить статус трека
                track_result = await db.execute(
                    select(PersonalizedTrack.status, PersonalizedTrack.error_message,
                           PersonalizedTrack.generation_duration_sec, PersonalizedTrack.generation_metadata)
                    .where(PersonalizedTrack.id == track_id)
                )
                row = track_result.one_or_none()

            if not row:
                yield _make_sse("error", {"error": "Track not found"})
                return

            track_status, error_msg, duration, metadata = row

            if track_status == "completed":
                total_tokens = 0
                if metadata:
                    total_tokens = metadata.get("total_tokens", 0)
                yield _make_sse("complete", {
                    "total_duration_sec": duration,
                    "total_tokens": total_tokens,
                })
                return

            if track_status == "failed":
                failed_step = None
                for step_name in ALL_STEPS:
                    if step_name not in completed_step_names:
                        failed_step = STEP_SHORT_NAMES.get(step_name, step_name)
                        break
                yield _make_sse("error", {
                    "error": error_msg or "Generation failed",
                    "failed_step": failed_step,
                })
                return

            if track_status == "cancelled":
                completed_steps = [
                    STEP_SHORT_NAMES.get(s, s) for s in ALL_STEPS if s in completed_step_names
                ]
                yield _make_sse("cancelled", {
                    "completed_steps": completed_steps,
                    "last_step": completed_steps[-1] if completed_steps else None,
                })
                return

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        # Timeout
        yield _make_sse("error", {"error": "Progress polling timeout"})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/batch/{batch_id}/progress")
async def get_batch_progress(
    batch_id: uuid.UUID,
):
    """SSE endpoint для прогресса batch-генерации.
    Использует собственные сессии (не DI), т.к. генератор живёт дольше запроса.
    """
    async def event_generator():
        timeout_seconds = 600
        elapsed = 0.0
        poll_interval = 2.0
        last_seen: dict[str, set[str]] = {}  # track_id_str → set of step_names

        # Получить все треки batch
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PersonalizedTrack)
                .where(PersonalizedTrack.batch_id == batch_id)
                .order_by(PersonalizedTrack.batch_index)
            )
            tracks = result.scalars().all()

        if not tracks:
            yield _make_sse("error", {"error": "Batch not found"})
            return

        track_ids = [t.id for t in tracks]
        track_id_strs = [str(t.id) for t in tracks]
        for tid_str in track_id_strs:
            last_seen[tid_str] = set()

        while elapsed < timeout_seconds:
            async with AsyncSessionLocal() as db:
                # Получить логи для всех треков batch
                log_result = await db.execute(
                    select(GenerationLog)
                    .where(GenerationLog.track_id.in_(track_ids))
                    .order_by(GenerationLog.created_at)
                )
                logs = log_result.scalars().all()

                # Отправить новые события
                for log in logs:
                    tid_str = str(log.track_id)
                    if log.step_name not in last_seen.get(tid_str, set()):
                        last_seen.setdefault(tid_str, set()).add(log.step_name)
                        short = STEP_SHORT_NAMES.get(log.step_name, log.step_name)
                        tokens_used = 0
                        if log.llm_calls:
                            for call in log.llm_calls:
                                tokens_used += call.get("tokens_used", 0)

                        yield _make_sse("step_update", {
                            "track_id": tid_str,
                            "batch_index": track_id_strs.index(tid_str),
                            "step": short,
                            "status": "completed",
                            "description": STEP_DESCRIPTIONS.get(log.step_name, log.step_name),
                            "duration_sec": log.step_duration_sec,
                            "tokens_used": tokens_used,
                            "summary": _step_summary(log.step_name, log.step_output or {}),
                        })

                # Проверить статусы всех треков
                track_result = await db.execute(
                    select(PersonalizedTrack)
                    .where(PersonalizedTrack.batch_id == batch_id)
                )
                current_tracks = track_result.scalars().all()

            all_done = all(t.status in ("completed", "failed", "cancelled") for t in current_tracks)

            if all_done:
                results_summary = []
                for t in sorted(current_tracks, key=lambda x: x.batch_index or 0):
                    results_summary.append({
                        "track_id": str(t.id),
                        "batch_index": t.batch_index,
                        "status": t.status,
                        "duration_sec": t.generation_duration_sec,
                    })
                yield _make_sse("batch_complete", {
                    "results": results_summary,
                })
                return

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        yield _make_sse("error", {"error": "Batch progress polling timeout"})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{track_id}", response_model=TrackDetail)
async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TrackDetail:
    """Получает детальную информацию о треке."""
    track = await track_service.get_track(track_id, db)

    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found",
        )

    return track


@router.get("/", response_model=TrackListResponse)
async def list_tracks(
    profile_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> TrackListResponse:
    """Получает список треков с фильтрацией и пагинацией."""
    return await track_service.list_tracks(
        db=db,
        profile_id=profile_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get("/{track_id}/field-usage", response_model=FieldUsageResponse)
async def get_track_field_usage(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> FieldUsageResponse:
    """Анализирует использование полей профиля в треке."""
    try:
        return await field_usage_service.get_field_usage(track_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
