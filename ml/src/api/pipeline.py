"""
Роутер для запуска pipeline генерации персонализированных треков.

Предоставляет endpoints:
- POST /pipeline/run - синхронный запуск pipeline
- POST /pipeline/run-batch - batch запуск N pipeline параллельно
"""

from fastapi import APIRouter, HTTPException, status

from ml.src.schemas.pipeline import (
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineBatchRequest,
    PipelineBatchResponse,
    PipelineError,
)
from ml.src.services.pipeline_orchestrator import (
    run_pipeline,
    run_pipeline_batch,
    PipelineCancelled,
)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline_sync(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Синхронный запуск pipeline генерации трека.

    Выполняет полный цикл B1-B8 и возвращает результат.
    Если трек отменён пользователем, возвращает 499.
    """
    from uuid import UUID

    try:
        track_id = UUID(request.track_id)
        result = await run_pipeline(request.profile, track_id, request.algorithm_version)
        return result
    except PipelineCancelled as e:
        raise HTTPException(
            status_code=499,  # Client Closed Request
            detail=f"Pipeline cancelled after steps: {', '.join(e.completed_steps)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution failed: {str(e)}",
        )


@router.post("/run-batch", response_model=PipelineBatchResponse)
async def run_pipeline_batch_endpoint(request: PipelineBatchRequest) -> PipelineBatchResponse:
    """
    Batch запуск pipeline для N треков.

    Запускает N генераций параллельно и возвращает массив результатов.
    """
    from uuid import UUID

    try:
        track_ids = [UUID(tid) for tid in request.track_ids]
        result = await run_pipeline_batch(
            request.profile, track_ids, request.algorithm_version
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch pipeline execution failed: {str(e)}",
        )
