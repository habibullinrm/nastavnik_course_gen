"""Инъекция реальных данных профиля в любую версию промпта.

Заменяет секции данных (между метками) на реальные данные из профиля
сессии и результатов предыдущих шагов. Работает для baseline и
пользовательских версий промптов.
"""

import logging
import re
from typing import Any

from ml.src.prompts.json_utils import to_json

logger = logging.getLogger(__name__)

# Маппинг шагов на секции данных: (start_label, end_label)
# Контент между start_label и end_label будет заменён реальными данными.
STEP_SECTIONS: dict[str, list[tuple[str, str]]] = {
    "B1_validate": [
        ("INPUT PROFILE:", "TASK:"),
    ],
    "B2_competencies": [
        ("VALIDATED PROFILE:", "FULL PROFILE DATA:"),
        ("FULL PROFILE DATA:", "TASK:"),
    ],
    "B3_ksa_matrix": [
        ("PROFILE CONTEXT:", "COMPETENCIES DATA:"),
        ("COMPETENCIES DATA:", "TASK:"),
    ],
    "B4_learning_units": [
        ("KSA MATRIX DATA:", "TASK:"),
    ],
    "B5_hierarchy": [
        ("LEARNING UNITS & CLUSTERS DATA:", "TIME CONSTRAINTS:"),
        ("TIME CONSTRAINTS:", "TASK:"),
    ],
    "B6_problem_formulations": [
        ("CLUSTERS DATA:", "TASK:"),
    ],
    "B7_schedule": [
        ("HIERARCHY & SEQUENCING DATA:", "LESSON BLUEPRINTS DATA:"),
        ("LESSON BLUEPRINTS DATA:", "LEARNER SCHEDULE DATA:"),
        ("LEARNER SCHEDULE DATA:", "TARGET:"),
        ("TARGET:", "TASK:"),
    ],
    "B8_validation": [
        ("ORIGINAL PROFILE DATA:", "COMPLETE TRACK DATA:"),
        ("COMPLETE TRACK DATA:", "TASK:"),
    ],
}


def _replace_section(text: str, start_label: str, end_label: str, new_content: str) -> str:
    """Заменить контент между start_label и end_label на new_content.

    Ищет паттерн: start_label<любой контент>end_label
    Заменяет на: start_label\n<new_content>\n\nend_label
    """
    pattern = re.compile(
        re.escape(start_label) + r".*?" + re.escape(end_label),
        re.DOTALL,
    )
    replacement = f"{start_label}\n{new_content}\n\n{end_label}"
    result, count = pattern.subn(replacement, text, count=1)
    if count == 0:
        logger.warning(
            "Section '%s' → '%s' not found in prompt, skipping injection",
            start_label,
            end_label,
        )
    return result


def inject_real_data(
    prompt_text: str,
    step_name: str,
    profile: dict[str, Any],
    input_data: dict[str, Any] | None = None,
) -> str:
    """Инъектировать реальные данные в промпт, заменяя секции данных.

    Args:
        prompt_text: Текст промпта (любая версия)
        step_name: Имя шага (B1_validate, B2_competencies, ...)
        profile: Профиль студента
        input_data: Результаты предыдущих шагов и профиль

    Returns:
        Промпт с реальными данными. При ошибке — оригинальный текст.
    """
    try:
        injector = _STEP_INJECTORS.get(step_name)
        if not injector:
            logger.warning("No injector for step %s, returning original prompt", step_name)
            return prompt_text
        return injector(prompt_text, profile, input_data or {})
    except Exception:
        logger.exception("Failed to inject data for step %s, returning original", step_name)
        return prompt_text


# ============================================================================
# Инъекторы для каждого шага
# ============================================================================


def _inject_b1(text: str, profile: dict, input_data: dict) -> str:
    profile_json = to_json(profile)
    return _replace_section(text, "INPUT PROFILE:", "TASK:", profile_json)


def _inject_b2(text: str, profile: dict, input_data: dict) -> str:
    b1 = input_data.get("B1_validate", {})
    orig_profile = b1.get("original_profile") or profile
    effective_level = b1.get("effective_level", profile.get("experience_level", "beginner"))

    summary = (
        f"- Topic: {orig_profile.get('topic')}\n"
        f"- Effective Level: {effective_level}\n"
        f"- Peak Task: {orig_profile.get('peak_task_id')}\n"
        f"- Target Tasks: {len(orig_profile.get('target_tasks', []))}\n"
        f"- Desired Outcomes: {orig_profile.get('desired_outcomes')}"
    )
    text = _replace_section(text, "VALIDATED PROFILE:", "FULL PROFILE DATA:", summary)

    profile_json = to_json(orig_profile)
    text = _replace_section(text, "FULL PROFILE DATA:", "TASK:", profile_json)
    return text


def _inject_b3(text: str, profile: dict, input_data: dict) -> str:
    context = (
        f"- Topic: {profile.get('topic')}\n"
        f"- Confusing Concepts: {len(profile.get('confusing_concepts', []))}\n"
        f"- Subtasks: {len(profile.get('subtasks', []))}\n"
        f"- Barriers: {len(profile.get('key_barriers', []))}"
    )
    text = _replace_section(text, "PROFILE CONTEXT:", "COMPETENCIES DATA:", context)

    b2 = input_data.get("B2_competencies", {})
    text = _replace_section(text, "COMPETENCIES DATA:", "TASK:", to_json(b2))
    return text


def _inject_b4(text: str, profile: dict, input_data: dict) -> str:
    b3 = input_data.get("B3_ksa_matrix", {})
    return _replace_section(text, "KSA MATRIX DATA:", "TASK:", to_json(b3))


def _inject_b5(text: str, profile: dict, input_data: dict) -> str:
    b4 = input_data.get("B4_learning_units", {})
    text = _replace_section(text, "LEARNING UNITS & CLUSTERS DATA:", "TIME CONSTRAINTS:", to_json(b4))

    b1 = input_data.get("B1_validate", {})
    time_budget = b1.get("weekly_time_budget_minutes") or profile.get("weekly_hours", 5) * 60
    weeks = b1.get("estimated_weeks") or 12
    weekly_budget = time_budget // weeks if weeks > 0 else 0
    time_text = (
        f"- Total time budget: {time_budget} minutes ({time_budget // 60} hours)\n"
        f"- Target weeks: {weeks}\n"
        f"- Weekly budget: {weekly_budget} minutes/week"
    )
    text = _replace_section(text, "TIME CONSTRAINTS:", "TASK:", time_text)
    return text


def _inject_b6(text: str, profile: dict, input_data: dict) -> str:
    b4 = input_data.get("B4_learning_units", {})
    clusters = b4.get("clusters", b4)
    return _replace_section(text, "CLUSTERS DATA:", "TASK:", to_json(clusters))


def _inject_b7(text: str, profile: dict, input_data: dict) -> str:
    b5 = input_data.get("B5_hierarchy", {})
    text = _replace_section(text, "HIERARCHY & SEQUENCING DATA:", "LESSON BLUEPRINTS DATA:", to_json(b5))

    b6 = input_data.get("B6_problem_formulations", {})
    text = _replace_section(text, "LESSON BLUEPRINTS DATA:", "LEARNER SCHEDULE DATA:", to_json(b6))

    schedule_info = {"weekly_hours": profile.get("weekly_hours", 5)}
    text = _replace_section(text, "LEARNER SCHEDULE DATA:", "TARGET:", to_json(schedule_info))

    total_weeks = b5.get("total_weeks", 12)
    text = _replace_section(text, "TARGET:", "TASK:", f"{total_weeks} weeks")
    return text


def _inject_b8(text: str, profile: dict, input_data: dict) -> str:
    text = _replace_section(text, "ORIGINAL PROFILE DATA:", "COMPLETE TRACK DATA:", to_json(profile))

    complete_track = {}
    for dep_step in [
        "B1_validate", "B2_competencies", "B3_ksa_matrix",
        "B4_learning_units", "B5_hierarchy", "B6_problem_formulations",
        "B7_schedule",
    ]:
        if dep_step in input_data:
            complete_track[dep_step] = input_data[dep_step]
    text = _replace_section(text, "COMPLETE TRACK DATA:", "TASK:", to_json(complete_track))
    return text


_STEP_INJECTORS: dict[str, callable] = {
    "B1_validate": _inject_b1,
    "B2_competencies": _inject_b2,
    "B3_ksa_matrix": _inject_b3,
    "B4_learning_units": _inject_b4,
    "B5_hierarchy": _inject_b5,
    "B6_problem_formulations": _inject_b6,
    "B7_schedule": _inject_b7,
    "B8_validation": _inject_b8,
}
