"""
API endpoints для тестирования отдельных шагов B1-B8.

Позволяет запускать каждый шаг изолированно с mock или real LLM client
для быстрой отладки промптов без прогона полного пайплайна.
"""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import ValidationError

from ml.src.pipeline.b1_validate import run_b1_validate
from ml.src.pipeline.b2_competencies import run_b2_competencies
from ml.src.pipeline.b3_ksa_matrix import run_b3_ksa_matrix
from ml.src.pipeline.b4_learning_units import run_b4_learning_units
from ml.src.pipeline.b5_hierarchy import run_b5_hierarchy
from ml.src.pipeline.b6_problem_formulations import run_b6_problem_formulations
from ml.src.pipeline.b7_schedule import run_b7_schedule
from ml.src.pipeline.b8_validation import run_b8_validation
from ml.src.schemas.step_testing import StepTestRequest, StepTestResponse
from ml.src.services.deepseek_client import DeepSeekClient
from ml.src.services.mock_llm_client import MockLLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps", tags=["step-testing"])


def get_llm_client(
    use_mock: bool, step_name: str | None = None
) -> DeepSeekClient | MockLLMClient:
    """
    Создать LLM client (Mock или DeepSeek) в зависимости от флага.

    Args:
        use_mock: True для MockLLMClient, False для DeepSeekClient
        step_name: Explicit step name for MockLLMClient (e.g., 'B1_validate')

    Returns:
        LLM client с методом chat_completion
    """
    if use_mock:
        return MockLLMClient(
            fixtures_dir="tests/fixtures/mock_responses", fixed_step_name=step_name
        )
    else:
        return DeepSeekClient()


@router.post("/b1", response_model=StepTestResponse)
async def test_b1_validate_profile(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B1: Profile Validation and Enrichment."""
    try:
        client = get_llm_client(request.use_mock, step_name="B1_validate")
        profile = request.inputs["profile"]
        result, metadata = await run_b1_validate(profile, client)

        return StepTestResponse(
            step_name="B1",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B1 test failed")
        return StepTestResponse(
            step_name="B1",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b2", response_model=StepTestResponse)
async def test_b2_competencies(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B2: Competency Formulation."""
    try:
        client = get_llm_client(request.use_mock, step_name="B2_competencies")
        validated_profile = request.inputs["validated_profile"]
        result, metadata = await run_b2_competencies(validated_profile, client)

        return StepTestResponse(
            step_name="B2",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B2 test failed")
        return StepTestResponse(
            step_name="B2",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b3", response_model=StepTestResponse)
async def test_b3_ksa_matrix(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B3: KSA Matrix."""
    try:
        client = get_llm_client(request.use_mock, step_name="B3_ksa_matrix")
        profile = request.inputs["profile"]
        competencies = request.inputs["competencies"]
        result, metadata = await run_b3_ksa_matrix(profile, competencies, client)

        return StepTestResponse(
            step_name="B3",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B3 test failed")
        return StepTestResponse(
            step_name="B3",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b4", response_model=StepTestResponse)
async def test_b4_learning_units(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B4: Learning Units Design."""
    try:
        client = get_llm_client(request.use_mock, step_name="B4_learning_units")
        ksa_matrix = request.inputs["ksa_matrix"]
        result, metadata = await run_b4_learning_units(ksa_matrix, client)

        return StepTestResponse(
            step_name="B4",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B4 test failed")
        return StepTestResponse(
            step_name="B4",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b5", response_model=StepTestResponse)
async def test_b5_hierarchy(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B5: Hierarchy and Levels."""
    try:
        client = get_llm_client(request.use_mock, step_name="B5_hierarchy")
        learning_units = request.inputs["learning_units"]
        time_budget_minutes = request.inputs["time_budget_minutes"]
        estimated_weeks = request.inputs["estimated_weeks"]
        result, metadata = await run_b5_hierarchy(
            learning_units, time_budget_minutes, estimated_weeks, client
        )

        return StepTestResponse(
            step_name="B5",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B5 test failed")
        return StepTestResponse(
            step_name="B5",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b6", response_model=StepTestResponse)
async def test_b6_problem_formulations(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B6: Problem Formulations."""
    try:
        client = get_llm_client(request.use_mock, step_name="B6_problem_formulations")
        clusters = request.inputs["clusters"]
        units = request.inputs["units"]
        result, metadata = await run_b6_problem_formulations(clusters, units, client)

        return StepTestResponse(
            step_name="B6",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B6 test failed")
        return StepTestResponse(
            step_name="B6",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b7", response_model=StepTestResponse)
async def test_b7_schedule(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B7: Schedule Assembly."""
    try:
        client = get_llm_client(request.use_mock, step_name="B7_schedule")
        hierarchy = request.inputs["hierarchy"]
        blueprints = request.inputs["blueprints"]
        profile = request.inputs["profile"]
        total_weeks = request.inputs["total_weeks"]
        result, metadata = await run_b7_schedule(
            hierarchy, blueprints, profile, total_weeks, client
        )

        return StepTestResponse(
            step_name="B7",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B7 test failed")
        return StepTestResponse(
            step_name="B7",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )


@router.post("/b8", response_model=StepTestResponse)
async def test_b8_validation(request: StepTestRequest) -> StepTestResponse:
    """Тестирование B8: Track Validation."""
    try:
        client = get_llm_client(request.use_mock, step_name="B8_validation")
        complete_track = request.inputs["complete_track"]
        profile = request.inputs["profile"]
        max_retries = request.inputs.get("max_retries", 3)
        result, metadata = await run_b8_validation(
            complete_track, profile, client, max_retries
        )

        return StepTestResponse(
            step_name="B8",
            success=True,
            output=result.model_dump(),
            metadata=metadata,
            error=None,
        )
    except Exception as e:
        logger.exception("B8 test failed")
        return StepTestResponse(
            step_name="B8",
            success=False,
            output={},
            metadata={},
            error=str(e),
        )
