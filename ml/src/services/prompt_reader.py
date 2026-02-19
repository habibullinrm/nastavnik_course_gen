"""Чтение baseline промптов из .py файлов."""

import inspect
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Маппинг шагов на функции генерации промптов
PROMPT_FUNCTIONS = {
    "B1_validate": ("ml.src.prompts.b1_prompt", "get_b1_prompt"),
    "B2_competencies": ("ml.src.prompts.b2_prompt", "get_b2_prompt"),
    "B3_ksa_matrix": ("ml.src.prompts.b3_prompt", "get_b3_prompt"),
    "B4_learning_units": ("ml.src.prompts.b4_prompt", "get_b4_prompt"),
    "B5_hierarchy": ("ml.src.prompts.b5_prompt", "get_b5_prompt"),
    "B6_problem_formulations": ("ml.src.prompts.b6_prompt", "get_b6_prompt"),
    "B7_schedule": ("ml.src.prompts.b7_prompt", "get_b7_prompt"),
    "B8_validation": ("ml.src.prompts.b8_prompt", "get_b8_prompt"),
}

# Пустой профиль-заглушка для рендеринга baseline
DUMMY_PROFILE: dict[str, Any] = {
    "topic": "Python programming",
    "subject_area": "Computer Science",
    "experience_level": "beginner",
    "desired_outcomes": ["Learn basics"],
    "target_tasks": [{"id": "t1", "title": "Write scripts"}],
    "subtasks": [{"id": "st1", "title": "Variables", "task_id": "t1"}],
    "confusing_concepts": [{"id": "c1", "concept": "OOP"}],
    "diagnostic_result": "gaps",
    "weekly_hours": 5,
    "success_criteria": ["Write code"],
}

# Dummy данные для шагов, требующих результаты предыдущих шагов
DUMMY_STEP_DATA: dict[str, dict[str, Any]] = {
    "B2_competencies": {
        "validated_profile": {
            "validation_status": "valid",
            "effective_level": "beginner",
            "estimated_weeks": 12,
            "weekly_time_budget_minutes": 300,
            "total_time_budget_minutes": 3600,
            "original_profile": DUMMY_PROFILE,
        }
    },
    "B3_ksa_matrix": {
        "competencies": {
            "competencies": [{"id": "c1", "title": "Basics", "description": "...",
                             "related_task_ids": ["t1"], "related_outcome_indices": [0],
                             "level": "foundational"}],
            "integral_competency_id": "c1",
            "competency_task_map": {}, "competency_outcome_map": {},
        }
    },
    "B5_hierarchy": {
        "learning_units": {"theory_units": [], "practice_units": [], "automation_units": [], "clusters": []},
        "time_budget_minutes": 300,
        "estimated_weeks": 12,
    },
    "B6_problem_formulations": {
        "clusters": [],
        "units": {"theory_units": [], "practice_units": [], "automation_units": [], "clusters": []},
    },
    "B7_schedule": {
        "hierarchy": {"levels": [], "unit_sequence": [], "time_compression_applied": False, "total_weeks": 12},
        "blueprints": {"blueprints": []},
        "schedule_info": {"weekly_hours": 5},
        "total_weeks": 12,
    },
    "B8_validation": {
        "complete_track": {},
        "profile": DUMMY_PROFILE,
    },
}


def _import_function(module_path: str, func_name: str):
    """Динамический импорт функции."""
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def get_baseline_prompt(step_name: str, profile: dict[str, Any] | None = None) -> str:
    """Получить baseline промпт для шага, используя dummy данные при необходимости."""
    if step_name not in PROMPT_FUNCTIONS:
        raise ValueError(f"Unknown step: {step_name}")

    module_path, func_name = PROMPT_FUNCTIONS[step_name]
    func = _import_function(module_path, func_name)

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    if not params:
        return func()

    p = profile or DUMMY_PROFILE
    dummy = DUMMY_STEP_DATA.get(step_name, {})

    # Построить аргументы, используя dummy данные для каждого параметра
    args = []
    for param_name in params:
        if param_name in dummy:
            args.append(dummy[param_name])
        elif param_name in ("profile",):
            args.append(p)
        else:
            # Для шагов без dummy — передать profile как единственный аргумент
            args.append(p)

    return func(*args)


def get_all_baselines(profile: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Получить все baseline промпты."""
    results = []
    for step_name, (module_path, func_name) in PROMPT_FUNCTIONS.items():
        try:
            prompt_text = get_baseline_prompt(step_name, profile)
            results.append({
                "step_name": step_name,
                "prompt_text": prompt_text,
                "function_name": func_name,
            })
        except Exception as e:
            logger.error(f"Failed to read baseline for {step_name}: {e}")
            results.append({
                "step_name": step_name,
                "prompt_text": f"ERROR: {e}",
                "function_name": func_name,
            })
    return results


def render_prompt(
    step_name: str,
    profile: dict[str, Any],
    extra_data: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    """
    Отрендерить промпт с данными профиля и результатами предыдущих шагов.

    extra_data может содержать:
      - ключи вида "B1_validate", "B2_competencies" и т.д. — результаты предыдущих шагов
      - profile — профиль (дублирует основной параметр)

    Returns:
        (rendered_prompt, variables_used)
    """
    prompt_text = _render_with_data(step_name, profile, extra_data)

    # Определить использованные переменные профиля
    variables_used = []
    for key in profile:
        key_str = str(key)
        if key_str in prompt_text:
            variables_used.append(key_str)

    return prompt_text, variables_used


def _render_with_data(
    step_name: str,
    profile: dict[str, Any],
    extra_data: dict[str, Any] | None = None,
) -> str:
    """Отрендерить промпт, используя реальные данные из extra_data вместо dummy."""
    if step_name not in PROMPT_FUNCTIONS:
        raise ValueError(f"Unknown step: {step_name}")

    module_path, func_name = PROMPT_FUNCTIONS[step_name]
    func = _import_function(module_path, func_name)

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    if not params:
        return func()

    # Маппинг параметров функций на данные из extra_data (результаты предыдущих шагов)
    step_data = _build_step_data(step_name, profile, extra_data or {})

    args = []
    for param_name in params:
        if param_name in step_data:
            args.append(step_data[param_name])
        elif param_name in ("profile",):
            args.append(profile)
        else:
            # Fallback на dummy данные
            dummy = DUMMY_STEP_DATA.get(step_name, {})
            args.append(dummy.get(param_name, profile))

    return func(*args)


def _build_step_data(
    step_name: str,
    profile: dict[str, Any],
    extra_data: dict[str, Any],
) -> dict[str, Any]:
    """Построить маппинг параметров из результатов предыдущих шагов."""
    data: dict[str, Any] = {}

    if step_name == "B1_validate":
        data["profile"] = profile

    elif step_name == "B2_competencies":
        b1 = extra_data.get("B1_validate")
        if b1:
            # B1 output intentionally excludes original_profile — inject it here
            validated = dict(b1)
            if not validated.get("original_profile"):
                validated["original_profile"] = profile
            data["validated_profile"] = validated

    elif step_name == "B3_ksa_matrix":
        data["profile"] = profile
        b2 = extra_data.get("B2_competencies")
        if b2:
            data["competencies"] = b2

    elif step_name == "B4_learning_units":
        b3 = extra_data.get("B3_ksa_matrix")
        if b3:
            data["ksa_matrix"] = b3

    elif step_name == "B5_hierarchy":
        b4 = extra_data.get("B4_learning_units")
        if b4:
            data["learning_units"] = b4
        b1 = extra_data.get("B1_validate")
        if b1:
            data["time_budget_minutes"] = b1.get("weekly_time_budget_minutes", 300)
            data["estimated_weeks"] = b1.get("estimated_weeks", 12)

    elif step_name == "B6_problem_formulations":
        b4 = extra_data.get("B4_learning_units")
        if b4:
            data["clusters"] = b4.get("clusters", [])
            data["units"] = b4

    elif step_name == "B7_schedule":
        b5 = extra_data.get("B5_hierarchy")
        if b5:
            data["hierarchy"] = b5
            data["total_weeks"] = b5.get("total_weeks", 12)
        b6 = extra_data.get("B6_problem_formulations")
        if b6:
            data["blueprints"] = b6
        data["schedule_info"] = {"weekly_hours": profile.get("weekly_hours", 5)}

    elif step_name == "B8_validation":
        # Собрать все результаты в один объект
        complete = {}
        for dep_step in [
            "B1_validate", "B2_competencies", "B3_ksa_matrix",
            "B4_learning_units", "B5_hierarchy", "B6_problem_formulations",
            "B7_schedule",
        ]:
            if dep_step in extra_data:
                complete[dep_step] = extra_data[dep_step]
        data["complete_track"] = complete
        data["profile"] = profile

    return data
