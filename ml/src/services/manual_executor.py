"""Manual step executor — выполнение одного шага с кастомным промптом."""

import json
import logging
import time
from typing import Any

from ml.src.schemas.pipeline_steps import (
    ValidatedStudentProfile,
    CompetencySet,
    KSAMatrix,
    LearningUnitsOutput,
    HierarchyOutput,
    BlueprintsOutput,
    ScheduleOutput,
    ValidationResult,
)
from ml.src.services.llm_client_factory import get_llm_client

logger = logging.getLogger(__name__)

# Маппинг шагов на Pydantic-модели ответов
STEP_RESPONSE_MODELS: dict[str, type] = {
    "B1_validate": ValidatedStudentProfile,
    "B2_competencies": CompetencySet,
    "B3_ksa_matrix": KSAMatrix,
    "B4_learning_units": LearningUnitsOutput,
    "B5_hierarchy": HierarchyOutput,
    "B6_problem_formulations": BlueprintsOutput,
    "B7_schedule": ScheduleOutput,
    "B8_validation": ValidationResult,
}

# Короткие имена для обратной совместимости
STEP_SHORT_TO_FULL = {
    "B1": "B1_validate",
    "B2": "B2_competencies",
    "B3": "B3_ksa_matrix",
    "B4": "B4_learning_units",
    "B5": "B5_hierarchy",
    "B6": "B6_problem_formulations",
    "B7": "B7_schedule",
    "B8": "B8_validation",
}


def normalize_step_name(step: str) -> str:
    """Нормализация имени шага (B1 → B1_validate)."""
    return STEP_SHORT_TO_FULL.get(step, step)


async def execute_step(
    step_name: str,
    prompt: str,
    input_data: dict[str, Any] | None = None,
    llm_params: dict[str, Any] | None = None,
    use_mock: bool = True,
) -> dict[str, Any]:
    """
    Выполнить один шаг pipeline с кастомным промптом.

    Args:
        step_name: Имя шага (B1_validate, B2_competencies, ...)
        prompt: Полный текст промпта (уже отрендеренный)
        input_data: Входные данные (для контекста, не используются напрямую)
        llm_params: Параметры LLM {temperature, max_tokens, model}
        use_mock: Использовать mock клиент

    Returns:
        {raw_response, parsed_result, tokens_used, duration_ms, model, parse_error}
    """
    step_name = normalize_step_name(step_name)
    params = llm_params or {}
    temperature = params.get("temperature", 0.3)
    max_tokens = params.get("max_tokens", 8000)

    response_model = STEP_RESPONSE_MODELS.get(step_name)
    if not response_model:
        return {
            "raw_response": None,
            "parsed_result": None,
            "tokens_used": 0,
            "duration_ms": 0,
            "model": "unknown",
            "parse_error": f"Unknown step: {step_name}",
        }

    client = await get_llm_client(mock_mode=use_mock)
    start_time = time.time()

    try:
        # MockLLMClient принимает step_name, DeepSeekClient — нет
        kwargs: dict[str, Any] = {
            "prompt": prompt,
            "response_model": response_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if use_mock:
            kwargs["step_name"] = step_name

        result, metadata = await client.chat_completion(**kwargs)
        duration_ms = (time.time() - start_time) * 1000

        parsed = result.model_dump() if hasattr(result, "model_dump") else result

        logger.info(
            f"Manual execute {step_name}: {metadata.get('tokens_used', 0)} tokens, "
            f"{duration_ms:.0f}ms"
        )

        return {
            "raw_response": metadata.get("raw_response", ""),
            "parsed_result": parsed,
            "tokens_used": metadata.get("tokens_used", 0),
            "duration_ms": duration_ms,
            "model": metadata.get("model", "unknown"),
            "parse_error": None,
        }

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"Manual execute {step_name} failed: {e}")
        return {
            "raw_response": None,
            "parsed_result": None,
            "tokens_used": 0,
            "duration_ms": duration_ms,
            "model": "error",
            "parse_error": str(e),
        }
