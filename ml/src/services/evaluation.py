"""Авто-метрики и LLM-as-Judge для оценки качества результатов."""

import logging
from typing import Any

from ml.src.services.manual_executor import STEP_RESPONSE_MODELS, normalize_step_name

logger = logging.getLogger(__name__)


def compute_auto_metrics(
    step_name: str,
    parsed_result: dict[str, Any],
    input_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Вычислить авто-метрики для результата шага.

    Метрики:
    - schema_compliance: соответствует ли Pydantic-схеме
    - field_coverage: % заполненных полей
    - step-specific метрики
    """
    step_name = normalize_step_name(step_name)
    metrics: dict[str, Any] = {}

    # Schema compliance
    model_class = STEP_RESPONSE_MODELS.get(step_name)
    if model_class:
        try:
            model_class.model_validate(parsed_result)
            metrics["schema_compliance"] = True
        except Exception as e:
            metrics["schema_compliance"] = False
            metrics["schema_errors"] = str(e)
    else:
        metrics["schema_compliance"] = None

    # Field coverage
    if model_class:
        expected_fields = set(model_class.model_fields.keys())
        present_fields = {
            k for k, v in parsed_result.items()
            if v is not None and v != [] and v != {}
        }
        coverage = len(present_fields & expected_fields) / max(len(expected_fields), 1)
        metrics["field_coverage"] = round(coverage, 2)
        metrics["missing_fields"] = list(expected_fields - present_fields)

    # Step-specific metrics
    if step_name == "B2_competencies":
        comps = parsed_result.get("competencies", [])
        metrics["competencies_count"] = len(comps)
        metrics["has_integral"] = bool(parsed_result.get("integral_competency_id"))
    elif step_name == "B3_ksa_matrix":
        metrics["knowledge_count"] = len(parsed_result.get("knowledge_items", []))
        metrics["skills_count"] = len(parsed_result.get("skill_items", []))
        metrics["habits_count"] = len(parsed_result.get("habit_items", []))
    elif step_name == "B4_learning_units":
        metrics["clusters_count"] = len(parsed_result.get("clusters", []))
        metrics["theory_units"] = len(parsed_result.get("theory_units", []))
        metrics["practice_units"] = len(parsed_result.get("practice_units", []))
    elif step_name == "B5_hierarchy":
        metrics["levels_count"] = len(parsed_result.get("levels", []))
        metrics["total_weeks"] = parsed_result.get("total_weeks")
    elif step_name == "B7_schedule":
        metrics["weeks_count"] = len(parsed_result.get("weeks", []))
        metrics["checkpoints_count"] = len(parsed_result.get("checkpoints", []))
    elif step_name == "B8_validation":
        metrics["overall_valid"] = parsed_result.get("overall_valid")
        metrics["critical_failures"] = parsed_result.get("critical_failures", 0)

    return metrics


async def run_llm_judge(
    step_name: str,
    parsed_result: dict[str, Any],
    input_data: dict[str, Any] | None = None,
    use_mock: bool = True,
) -> dict[str, Any]:
    """
    LLM-as-Judge оценка качества результата.

    Возвращает {score: 1-10, reasoning: str}
    """
    if use_mock:
        return {
            "score": 7,
            "reasoning": "Mock LLM Judge: результат выглядит корректным, "
            "структура соответствует ожиданиям, покрытие полей достаточное.",
        }

    # Real LLM judge
    from ml.src.services.llm_client_factory import get_llm_client
    import json

    client = await get_llm_client(mock_mode=False)

    judge_prompt = f"""You are evaluating the output of pipeline step {step_name}.

RESULT TO EVALUATE:
{json.dumps(parsed_result, ensure_ascii=False, indent=2)[:4000]}

INPUT DATA:
{json.dumps(input_data or {}, ensure_ascii=False, indent=2)[:2000]}

Rate the quality on a scale of 1-10 and explain your reasoning.
Return JSON: {{"score": <1-10>, "reasoning": "<explanation>"}}
"""

    try:
        from pydantic import BaseModel

        class JudgeResult(BaseModel):
            score: int
            reasoning: str

        result, _ = await client.chat_completion(
            prompt=judge_prompt,
            response_model=JudgeResult,
            temperature=0.3,
            max_tokens=1000,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"LLM Judge failed: {e}")
        return {"score": 0, "reasoning": f"Judge error: {e}"}
