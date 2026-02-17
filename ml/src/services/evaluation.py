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

    Возвращает {score, summary, strengths, problems, suggestions, reasoning}
    """
    from ml.src.prompts.judge_prompt import get_judge_prompt

    normalized = normalize_step_name(step_name)

    if use_mock:
        return _mock_judge_response(normalized, parsed_result)

    from ml.src.services.llm_client_factory import get_llm_client

    client = await get_llm_client(mock_mode=False)
    judge_prompt_text = get_judge_prompt(normalized, parsed_result, input_data)

    try:
        from pydantic import BaseModel

        class JudgeResult(BaseModel):
            score: int
            summary: str = ""
            strengths: list[str] = []
            problems: list[str] = []
            suggestions: list[str] = []
            reasoning: str = ""

        result, _ = await client.chat_completion(
            prompt=judge_prompt_text,
            response_model=JudgeResult,
            temperature=0.3,
            max_tokens=2000,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"LLM Judge failed: {e}")
        return {
            "score": 0,
            "summary": f"Ошибка Judge: {e}",
            "strengths": [],
            "problems": [str(e)],
            "suggestions": [],
            "reasoning": f"Не удалось выполнить оценку: {e}",
        }


def _mock_judge_response(
    step_name: str, parsed_result: dict[str, Any]
) -> dict[str, Any]:
    """Сгенерировать mock-ответ Judge с базовым анализом."""
    problems: list[str] = []
    strengths: list[str] = []
    suggestions: list[str] = []
    score = 7

    # Базовые проверки по структуре
    if not parsed_result:
        return {
            "score": 1,
            "summary": "Результат пустой — генерация не вернула данных.",
            "strengths": [],
            "problems": ["Результат пустой или None"],
            "suggestions": ["Проверить промпт и входные данные"],
            "reasoning": "Пустой результат не подлежит оценке.",
        }

    # Step-specific mock analysis
    if step_name == "B1_validate":
        if parsed_result.get("validation_status") == "valid":
            strengths.append("Профиль прошёл валидацию без ошибок")
        elif parsed_result.get("validation_status") == "valid_with_warnings":
            strengths.append("Профиль валиден, есть предупреждения")
            warnings = parsed_result.get("validation_warnings", [])
            if warnings:
                problems.append(f"Обнаружено {len(warnings)} предупреждений")
        else:
            problems.append("Профиль не прошёл валидацию")
            score -= 2

        weeks = parsed_result.get("estimated_weeks")
        if weeks and (weeks < 4 or weeks > 52):
            problems.append(f"estimated_weeks={weeks} вне диапазона 4-52")
            score -= 1

    elif step_name == "B2_competencies":
        comps = parsed_result.get("competencies", [])
        count = len(comps)
        if count < 3:
            problems.append(f"Слишком мало компетенций: {count} (ожидается >= 3)")
            score -= 2
        elif count > 15:
            problems.append(f"Слишком много компетенций: {count} (ожидается <= 15)")
            score -= 1
        else:
            strengths.append(f"Адекватное количество компетенций: {count}")

        if not parsed_result.get("integral_competency_id"):
            problems.append("Отсутствует интегративная компетенция (integral_competency_id)")
            score -= 1
        else:
            strengths.append("Есть интегративная компетенция")

        task_map = parsed_result.get("competency_task_map", {})
        if not task_map:
            problems.append("Пустая competency_task_map — компетенции не привязаны к задачам")
            score -= 1

    elif step_name == "B3_ksa_matrix":
        k = len(parsed_result.get("knowledge_items", []))
        s = len(parsed_result.get("skill_items", []))
        h = len(parsed_result.get("habit_items", []))
        if k == 0:
            problems.append("Нет knowledge items")
            score -= 2
        if s == 0:
            problems.append("Нет skill items")
            score -= 2
        if k > 0 and s > 0:
            strengths.append(f"KSA-матрица: {k} знаний, {s} навыков, {h} привычек")

    elif step_name == "B4_learning_units":
        clusters = len(parsed_result.get("clusters", []))
        if clusters == 0:
            problems.append("Нет кластеров")
            score -= 2
        else:
            strengths.append(f"Сформировано {clusters} кластеров")

    elif step_name == "B7_schedule":
        weeks = parsed_result.get("weeks", [])
        if len(weeks) == 0:
            problems.append("Расписание пустое — нет недель")
            score -= 3
        else:
            strengths.append(f"Расписание на {len(weeks)} недель")
        checkpoints = parsed_result.get("checkpoints", [])
        if not checkpoints:
            suggestions.append("Добавить контрольные точки (checkpoints)")

    elif step_name == "B8_validation":
        if parsed_result.get("overall_valid"):
            strengths.append("Итоговая валидация пройдена")
        else:
            problems.append("Итоговая валидация не пройдена")
            score -= 2
        cf = parsed_result.get("critical_failures", 0)
        if cf > 0:
            problems.append(f"Критических ошибок: {cf}")
            score -= cf

    if not strengths:
        strengths.append("Структура результата соответствует ожиданиям")
    if not suggestions:
        suggestions.append("Сравнить результат с предыдущими запусками для отслеживания регрессий")

    score = max(1, min(10, score))

    summary_parts = []
    if strengths:
        summary_parts.append(strengths[0])
    if problems:
        summary_parts.append(f"Найдено проблем: {len(problems)}")
    summary = ". ".join(summary_parts) + "."

    reasoning_parts = ["Mock Judge анализ:"]
    if strengths:
        reasoning_parts.append("Сильные стороны: " + "; ".join(strengths))
    if problems:
        reasoning_parts.append("Проблемы: " + "; ".join(problems))
    if suggestions:
        reasoning_parts.append("Рекомендации: " + "; ".join(suggestions))

    return {
        "score": score,
        "summary": summary,
        "strengths": strengths,
        "problems": problems,
        "suggestions": suggestions,
        "reasoning": " ".join(reasoning_parts),
    }
