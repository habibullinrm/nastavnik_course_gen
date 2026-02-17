"""Пре-процессор: проверяет наличие обязательных полей во входных данных."""

PROCESSOR_META = {
    "name": "validate_input_schema",
    "type": "pre",
    "applicable_steps": ["B1_validate", "B2_competencies", "B3_ksa_matrix"],
    "description": "Проверяет наличие обязательных полей во входных данных",
}

REQUIRED_FIELDS_BY_STEP = {
    "B1_validate": ["topic", "experience_level"],
    "B2_competencies": ["validation_status", "effective_level"],
    "B3_ksa_matrix": ["competencies"],
}


async def run(data: dict, step_name: str, config_params: dict | None = None) -> dict:
    required = REQUIRED_FIELDS_BY_STEP.get(step_name, [])
    missing = [f for f in required if f not in data or data[f] is None]

    if missing:
        return {
            "passed": False,
            "output": {"missing_fields": missing},
            "message": f"Отсутствуют поля: {', '.join(missing)}",
        }

    return {
        "passed": True,
        "output": {"checked_fields": required},
        "message": f"Все {len(required)} обязательных полей присутствуют",
    }
