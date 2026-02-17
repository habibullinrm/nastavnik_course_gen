"""
Router для ручного режима отладки промптов.

Endpoints:
- POST /manual/execute-step — выполнить шаг с кастомным промптом
- POST /manual/render-prompt — отрендерить промпт
- GET  /manual/prompts/baseline — прочитать baseline промпты
- GET  /manual/processors — список процессоров
- POST /manual/processors/run — запустить процессор
- POST /manual/evaluate — авто-метрики + LLM-as-Judge
"""

import importlib
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ml.src.schemas.manual import (
    ManualExecuteRequest,
    ManualExecuteResponse,
    RenderPromptRequest,
    RenderPromptResponse,
    BaselinePromptsResponse,
    BaselinePrompt,
    ProcessorsListResponse,
    ProcessorMeta,
    ProcessorRunRequest,
    ProcessorRunResponse,
    EvaluateRequest,
    EvaluateResponse,
)
from ml.src.services.manual_executor import execute_step
from ml.src.services.prompt_reader import get_all_baselines, render_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/manual", tags=["manual"])

PROCESSORS_DIR = Path("ml/processors/examples")


@router.post("/execute-step", response_model=ManualExecuteResponse)
async def manual_execute_step(request: ManualExecuteRequest) -> ManualExecuteResponse:
    """Выполнить один шаг с кастомным промптом."""
    result = await execute_step(
        step_name=request.step_name,
        prompt=request.prompt,
        input_data=request.input_data,
        llm_params=request.llm_params,
        use_mock=request.use_mock,
    )
    return ManualExecuteResponse(**result)


@router.post("/render-prompt", response_model=RenderPromptResponse)
async def manual_render_prompt(request: RenderPromptRequest) -> RenderPromptResponse:
    """Отрендерить промпт с данными профиля."""
    try:
        rendered, variables = render_prompt(
            request.step_name, request.profile, request.extra_data
        )
        return RenderPromptResponse(
            step_name=request.step_name,
            rendered_prompt=rendered,
            variables_used=variables,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prompts/baseline", response_model=BaselinePromptsResponse)
async def get_baseline_prompts() -> BaselinePromptsResponse:
    """Прочитать все baseline промпты из .py файлов."""
    baselines = get_all_baselines()
    prompts = [BaselinePrompt(**b) for b in baselines]
    return BaselinePromptsResponse(prompts=prompts)


@router.get("/processors", response_model=ProcessorsListResponse)
async def list_processors() -> ProcessorsListResponse:
    """Список доступных процессоров из ml/processors/."""
    processors = []
    processors_dir = PROCESSORS_DIR

    if not processors_dir.exists():
        return ProcessorsListResponse(processors=[])

    for py_file in processors_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            module_name = f"ml.processors.examples.{py_file.stem}"
            module = importlib.import_module(module_name)
            meta = getattr(module, "PROCESSOR_META", None)
            if meta:
                processors.append(ProcessorMeta(**meta))
        except Exception as e:
            logger.warning(f"Failed to load processor {py_file.name}: {e}")

    return ProcessorsListResponse(processors=processors)


@router.post("/processors/run", response_model=ProcessorRunResponse)
async def run_processor(request: ProcessorRunRequest) -> ProcessorRunResponse:
    """Запустить конкретный процессор."""
    try:
        module_name = f"ml.processors.examples.{request.processor_name}"
        module = importlib.import_module(module_name)
        run_fn = getattr(module, "run", None)
        if not run_fn:
            raise HTTPException(
                status_code=400,
                detail=f"Processor {request.processor_name} has no 'run' function",
            )

        result = await run_fn(
            data=request.data,
            step_name=request.step_name,
            config_params=request.config_params,
        )

        return ProcessorRunResponse(
            name=request.processor_name,
            passed=result.get("passed", False),
            output=result.get("output"),
            message=result.get("message"),
        )
    except HTTPException:
        raise
    except Exception as e:
        return ProcessorRunResponse(
            name=request.processor_name,
            passed=False,
            error=str(e),
        )


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_result(request: EvaluateRequest) -> EvaluateResponse:
    """Авто-метрики + опциональный LLM-as-Judge."""
    from ml.src.services.evaluation import compute_auto_metrics, run_llm_judge

    auto_eval = compute_auto_metrics(
        step_name=request.step_name,
        parsed_result=request.parsed_result,
        input_data=request.input_data,
    )

    llm_judge = None
    if request.run_llm_judge:
        llm_judge = await run_llm_judge(
            step_name=request.step_name,
            parsed_result=request.parsed_result,
            input_data=request.input_data,
            use_mock=request.use_mock,
        )

    return EvaluateResponse(
        auto_evaluation=auto_eval,
        llm_judge_evaluation=llm_judge,
    )
