"""Пост-процессор: проверяет количество компетенций B2."""

PROCESSOR_META = {
    "name": "check_competency_count",
    "type": "post",
    "applicable_steps": ["B2_competencies"],
    "description": "Проверяет, что компетенций >= 3 и <= 15",
}


async def run(data: dict, step_name: str, config_params: dict | None = None) -> dict:
    comps = data.get("competencies", [])
    count = len(comps)
    passed = 3 <= count <= 15
    return {"passed": passed, "output": {"count": count}, "message": f"{count} компетенций"}
