"""B6: Problem Formulations (Lesson Blueprints)."""

import logging
from typing import Any

from ml.src.prompts.b6_prompt import get_b6_prompt
from ml.src.schemas.pipeline_steps import BlueprintsOutput
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b6_problem_formulations(
    clusters: list[dict[str, Any]],
    units: dict[str, Any],
    deepseek_client: DeepSeekClient,
) -> tuple[BlueprintsOutput, dict[str, Any]]:
    """
    B6: Create PBL lesson blueprints for each cluster.

    Args:
        clusters: Cluster data from B4
        units: All units data from B4
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (blueprints, metadata)
    """
    logger.info("Starting B6: Problem formulations")

    prompt = get_b6_prompt(clusters, units)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=BlueprintsOutput,
        temperature=0.8,  # Higher creativity for problem design
        max_tokens=6000,
    )

    logger.info(f"B6 complete: {len(result.blueprints)} lesson blueprints created")

    return result, metadata
