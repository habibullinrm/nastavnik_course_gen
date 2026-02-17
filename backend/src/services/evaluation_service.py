"""Сервис авто-метрик оценки результатов шагов."""

import logging
from typing import Any

import httpx

from backend.src.core.config import settings

logger = logging.getLogger(__name__)

ML_URL = settings.ML_SERVICE_URL


async def compute_auto_evaluation(
    step_name: str,
    parsed_result: dict[str, Any],
    input_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Запросить авто-метрики у ML-сервиса."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ML_URL}/manual/evaluate",
            json={
                "step_name": step_name,
                "parsed_result": parsed_result,
                "input_data": input_data,
                "run_llm_judge": False,
            },
        )
        response.raise_for_status()
        data = response.json()
    return data.get("auto_evaluation", {})


async def run_llm_judge(
    step_name: str,
    parsed_result: dict[str, Any],
    input_data: dict[str, Any] | None = None,
    use_mock: bool = True,
) -> dict[str, Any]:
    """Запросить LLM-as-Judge оценку у ML-сервиса."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ML_URL}/manual/evaluate",
            json={
                "step_name": step_name,
                "parsed_result": parsed_result,
                "input_data": input_data,
                "run_llm_judge": True,
                "use_mock": use_mock,
            },
        )
        response.raise_for_status()
        data = response.json()
    return data.get("llm_judge_evaluation", {})
