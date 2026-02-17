"""
Router для ручного режима отладки промптов и pipeline.

Endpoints:
- POST/GET/PATCH/DELETE /api/manual/sessions — CRUD сессий
- POST /api/manual/sessions/{id}/steps/{step}/run — запуск шага
- GET /api/manual/sessions/{id}/steps — статус шагов
- GET /api/manual/sessions/{id}/steps/{step}/runs — история запусков
- GET /api/manual/sessions/{id}/runs/{run_id} — детали запуска
- PATCH /api/manual/sessions/{id}/runs/{run_id}/rating — оценка запуска
- GET/POST /api/manual/prompts — версии промптов
- POST /api/manual/prompts/load-baseline — загрузка baseline
- POST /api/manual/prompts/{step}/rollback/{version} — откат
- GET/PUT /api/manual/sessions/{id}/processors/{step} — процессоры
- GET /api/manual/processors — доступные процессоры
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db
from backend.src.schemas.manual import (
    ManualSessionCreate,
    ManualSessionUpdate,
    ManualSessionResponse,
    ManualSessionListResponse,
    PromptVersionCreate,
    PromptVersionResponse,
    PromptStepSummary,
    PromptListResponse,
    StepRunRequest,
    StepRunResponse,
    StepRunSummary,
    StepStatusResponse,
    UserRatingUpdate,
    ProcessorConfigUpdate,
    ProcessorConfigResponse,
    ProcessorConfigItem,
    ProcessorInfo,
)
from backend.src.services import manual_service, prompt_service, evaluation_service

router = APIRouter(prefix="/api/manual", tags=["manual"])


# ============================================================================
# Sessions
# ============================================================================


@router.post("/sessions", response_model=ManualSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: ManualSessionCreate,
    db: AsyncSession = Depends(get_db),
) -> ManualSessionResponse:
    """Создать новую сессию отладки."""
    try:
        session = await manual_service.create_session(
            profile_id=request.profile_id,
            name=request.name,
            description=request.description,
            db=db,
        )
        return ManualSessionResponse(
            id=session.id,
            profile_id=session.profile_id,
            profile_snapshot=session.profile_snapshot,
            name=session.name,
            description=session.description,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions", response_model=ManualSessionListResponse)
async def list_sessions(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ManualSessionListResponse:
    """Список сессий."""
    sessions, total = await manual_service.list_sessions(
        db=db, status=status_filter, limit=limit, offset=offset
    )
    return ManualSessionListResponse(
        sessions=[
            ManualSessionResponse(
                id=s.id, profile_id=s.profile_id, profile_snapshot=s.profile_snapshot,
                name=s.name, description=s.description, status=s.status,
                created_at=s.created_at, updated_at=s.updated_at,
            )
            for s in sessions
        ],
        total=total,
    )


@router.get("/sessions/{session_id}", response_model=ManualSessionResponse)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ManualSessionResponse:
    """Детали сессии."""
    session = await manual_service.get_session(session_id, db)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return ManualSessionResponse(
        id=session.id, profile_id=session.profile_id,
        profile_snapshot=session.profile_snapshot,
        name=session.name, description=session.description, status=session.status,
        created_at=session.created_at, updated_at=session.updated_at,
    )


@router.patch("/sessions/{session_id}", response_model=ManualSessionResponse)
async def update_session(
    session_id: uuid.UUID,
    request: ManualSessionUpdate,
    db: AsyncSession = Depends(get_db),
) -> ManualSessionResponse:
    """Обновить сессию."""
    try:
        session = await manual_service.update_session(
            session_id, db,
            name=request.name,
            description=request.description,
            status=request.status,
            profile_snapshot=request.profile_snapshot,
        )
        return ManualSessionResponse(
            id=session.id, profile_id=session.profile_id,
            profile_snapshot=session.profile_snapshot,
            name=session.name, description=session.description, status=session.status,
            created_at=session.created_at, updated_at=session.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Удалить сессию."""
    try:
        await manual_service.delete_session(session_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Steps
# ============================================================================


@router.post("/sessions/{session_id}/steps/{step_name}/run", response_model=StepRunResponse)
async def run_step(
    session_id: uuid.UUID,
    step_name: str,
    request: StepRunRequest,
    db: AsyncSession = Depends(get_db),
) -> StepRunResponse:
    """Запустить шаг."""
    try:
        run = await manual_service.run_step(
            session_id=session_id,
            step_name=step_name,
            db=db,
            prompt_version_id=request.prompt_version_id,
            custom_prompt=request.custom_prompt,
            input_data=request.input_data,
            llm_params=request.llm_params,
            run_preprocessors=request.run_preprocessors,
            run_postprocessors=request.run_postprocessors,
            use_mock=request.use_mock,
        )
        return _run_to_response(run)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step execution failed: {e}")


@router.get("/sessions/{session_id}/steps", response_model=StepStatusResponse)
async def get_steps_status(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StepStatusResponse:
    """Статус всех шагов в сессии."""
    steps = await manual_service.get_step_status(session_id, db)
    return StepStatusResponse(steps=steps)


@router.get("/sessions/{session_id}/steps/{step_name}/runs", response_model=list[StepRunSummary])
async def get_step_runs(
    session_id: uuid.UUID,
    step_name: str,
    db: AsyncSession = Depends(get_db),
) -> list[StepRunSummary]:
    """История запусков шага."""
    runs = await manual_service.get_step_runs(session_id, step_name, db)
    return [
        StepRunSummary(
            id=r.id, run_number=r.run_number, status=r.status,
            duration_ms=r.duration_ms, tokens_used=r.tokens_used,
            user_rating=r.user_rating, created_at=r.created_at,
        )
        for r in runs
    ]


@router.get("/sessions/{session_id}/runs/{run_id}", response_model=StepRunResponse)
async def get_run_detail(
    session_id: uuid.UUID,
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StepRunResponse:
    """Детали запуска."""
    run = await manual_service.get_run_by_id(run_id, db)
    if not run or run.session_id != session_id:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_response(run)


@router.patch("/sessions/{session_id}/runs/{run_id}/rating", response_model=StepRunResponse)
async def update_run_rating(
    session_id: uuid.UUID,
    run_id: uuid.UUID,
    request: UserRatingUpdate,
    db: AsyncSession = Depends(get_db),
) -> StepRunResponse:
    """Оценить запуск."""
    try:
        run = await manual_service.update_run_rating(
            run_id, request.user_rating, request.user_notes, db
        )
        return _run_to_response(run)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Prompts
# ============================================================================


@router.get("/prompts", response_model=PromptListResponse)
async def list_prompts(
    db: AsyncSession = Depends(get_db),
) -> PromptListResponse:
    """Все шаги с последней версией промпта."""
    steps = await prompt_service.get_all_steps_latest(db)
    return PromptListResponse(
        steps=[PromptStepSummary(**s) for s in steps]
    )


@router.post("/prompts/load-baseline", response_model=list[PromptVersionResponse])
async def load_baseline_prompts(
    db: AsyncSession = Depends(get_db),
) -> list[PromptVersionResponse]:
    """Загрузить baseline промпты из .py файлов."""
    versions = await prompt_service.load_baselines(db)
    return [
        PromptVersionResponse(
            id=v.id, step_name=v.step_name, version=v.version,
            prompt_text=v.prompt_text, change_description=v.change_description,
            is_baseline=v.is_baseline, created_at=v.created_at,
        )
        for v in versions
    ]


@router.get("/prompts/{step_name}/versions", response_model=list[PromptVersionResponse])
async def get_prompt_versions(
    step_name: str,
    db: AsyncSession = Depends(get_db),
) -> list[PromptVersionResponse]:
    """Все версии промпта для шага."""
    versions = await prompt_service.get_step_versions(step_name, db)
    return [
        PromptVersionResponse(
            id=v.id, step_name=v.step_name, version=v.version,
            prompt_text=v.prompt_text, change_description=v.change_description,
            is_baseline=v.is_baseline, created_at=v.created_at,
        )
        for v in versions
    ]


@router.post("/prompts/{step_name}", response_model=PromptVersionResponse, status_code=201)
async def create_prompt_version(
    step_name: str,
    request: PromptVersionCreate,
    db: AsyncSession = Depends(get_db),
) -> PromptVersionResponse:
    """Создать новую версию промпта."""
    version = await prompt_service.create_version(
        step_name=step_name,
        prompt_text=request.prompt_text,
        change_description=request.change_description,
        is_baseline=False,
        db=db,
    )
    return PromptVersionResponse(
        id=version.id, step_name=version.step_name, version=version.version,
        prompt_text=version.prompt_text, change_description=version.change_description,
        is_baseline=version.is_baseline, created_at=version.created_at,
    )


@router.post("/prompts/{step_name}/rollback/{version}", response_model=PromptVersionResponse)
async def rollback_prompt(
    step_name: str,
    version: int,
    db: AsyncSession = Depends(get_db),
) -> PromptVersionResponse:
    """Откатить к указанной версии промпта."""
    try:
        v = await prompt_service.rollback_to_version(step_name, version, db)
        return PromptVersionResponse(
            id=v.id, step_name=v.step_name, version=v.version,
            prompt_text=v.prompt_text, change_description=v.change_description,
            is_baseline=v.is_baseline, created_at=v.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Processors
# ============================================================================


@router.get("/processors", response_model=list[ProcessorInfo])
async def list_available_processors() -> list[ProcessorInfo]:
    """Доступные процессоры (из ML-сервиса)."""
    import httpx
    from backend.src.core.config import settings

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{settings.ML_SERVICE_URL}/manual/processors")
        resp.raise_for_status()
        data = resp.json()

    return [ProcessorInfo(**p) for p in data.get("processors", [])]


@router.get("/sessions/{session_id}/processors/{step_name}", response_model=ProcessorConfigResponse)
async def get_processor_config(
    session_id: uuid.UUID,
    step_name: str,
    db: AsyncSession = Depends(get_db),
) -> ProcessorConfigResponse:
    """Конфиг процессоров для шага."""
    configs = await manual_service.get_processor_configs(session_id, step_name, db)
    return ProcessorConfigResponse(
        step_name=step_name,
        processors=[
            ProcessorConfigItem(
                processor_name=c.processor_name,
                processor_type=c.processor_type,
                execution_order=c.execution_order,
                enabled=c.enabled,
                config_params=c.config_params,
            )
            for c in configs
        ],
    )


@router.put("/sessions/{session_id}/processors/{step_name}", response_model=ProcessorConfigResponse)
async def set_processor_config(
    session_id: uuid.UUID,
    step_name: str,
    request: ProcessorConfigUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProcessorConfigResponse:
    """Задать конфиг процессоров для шага."""
    configs = await manual_service.set_processor_configs(
        session_id, step_name,
        [p.model_dump() for p in request.processors],
        db,
    )
    return ProcessorConfigResponse(
        step_name=step_name,
        processors=[
            ProcessorConfigItem(
                processor_name=c.processor_name,
                processor_type=c.processor_type,
                execution_order=c.execution_order,
                enabled=c.enabled,
                config_params=c.config_params,
            )
            for c in configs
        ],
    )


# ============================================================================
# LLM Judge
# ============================================================================


@router.post("/sessions/{session_id}/runs/{run_id}/judge")
async def request_llm_judge(
    session_id: uuid.UUID,
    run_id: uuid.UUID,
    use_mock: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    """Запросить LLM-as-Judge оценку для запуска."""
    run = await manual_service.get_run_by_id(run_id, db)
    if not run or run.session_id != session_id:
        raise HTTPException(status_code=404, detail="Run not found")
    if not run.parsed_result:
        raise HTTPException(status_code=400, detail="No parsed result to evaluate")

    judge_result = await evaluation_service.run_llm_judge(
        step_name=run.step_name,
        parsed_result=run.parsed_result,
        input_data=run.input_data,
        use_mock=use_mock,
    )
    run.llm_judge_evaluation = judge_result
    await db.flush()

    return _run_to_response(run)


# ============================================================================
# Helpers
# ============================================================================


def _run_to_response(run) -> StepRunResponse:
    """Конвертировать ManualStepRun в StepRunResponse."""
    return StepRunResponse(
        id=run.id,
        session_id=run.session_id,
        step_name=run.step_name,
        run_number=run.run_number,
        prompt_version_id=run.prompt_version_id,
        rendered_prompt=run.rendered_prompt,
        input_data=run.input_data,
        profile_variables=run.profile_variables,
        llm_params=run.llm_params,
        raw_response=run.raw_response,
        parsed_result=run.parsed_result,
        parse_error=run.parse_error,
        tokens_used=run.tokens_used,
        duration_ms=run.duration_ms,
        status=run.status,
        preprocessor_results=run.preprocessor_results,
        postprocessor_results=run.postprocessor_results,
        auto_evaluation=run.auto_evaluation,
        llm_judge_evaluation=run.llm_judge_evaluation,
        user_rating=run.user_rating,
        user_notes=run.user_notes,
        created_at=run.created_at,
    )
