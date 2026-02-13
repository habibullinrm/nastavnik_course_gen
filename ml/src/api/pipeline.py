"""
Роутер для запуска pipeline генерации персонализированных треков.

Предоставляет endpoints:
- POST /pipeline/run - синхронный запуск pipeline
- POST /pipeline/run-stream - потоковый запуск с SSE прогрессом
"""

from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from ml.src.schemas.pipeline import PipelineRunRequest, PipelineRunResponse, PipelineError
from ml.src.services.pipeline_orchestrator import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline_sync(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Синхронный запуск pipeline генерации трека.

    Выполняет полный цикл B1-B8 и возвращает результат.

    Args:
        request: Профиль студента и параметры генерации

    Returns:
        PipelineRunResponse: Сгенерированный трек с метаданными

    Raises:
        HTTPException: 500 если pipeline упал с ошибкой
    """
    from uuid import UUID

    try:
        track_id = UUID(request.track_id)
        result = await run_pipeline(request.profile, track_id, request.algorithm_version)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}",
        )


async def _pipeline_stream(profile: dict) -> AsyncIterator[str]:
    """
    Генератор SSE событий для потокового выполнения pipeline.

    Отправляет события:
    - step_start: начало шага (B1-B8)
    - step_complete: завершение шага с результатом
    - error: ошибка на шаге
    - complete: финальный результат

    Args:
        profile: Профиль студента

    Yields:
        str: SSE события в формате "event: data\ndata: json\n\n"
    """
    import json
    from ml.src.services.pipeline_orchestrator import run_pipeline_with_progress

    try:
        async for event in run_pipeline_with_progress(profile):
            yield {
                "event": event["type"],
                "data": json.dumps(event["data"], ensure_ascii=False),
            }
    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps(
                {
                    "error": str(e),
                    "step": event.get("data", {}).get("step", "unknown"),
                },
                ensure_ascii=False,
            ),
        }


@router.post("/run-stream")
async def run_pipeline_stream(request: PipelineRunRequest) -> EventSourceResponse:
    """
    Потоковый запуск pipeline с SSE прогрессом.

    Отправляет события по мере выполнения шагов B1-B8.

    Args:
        request: Профиль студента и параметры генерации

    Returns:
        EventSourceResponse: SSE stream с прогрессом выполнения
    """
    return EventSourceResponse(_pipeline_stream(request.profile))
