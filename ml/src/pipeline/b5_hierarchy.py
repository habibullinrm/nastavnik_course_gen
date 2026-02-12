"""B5: Hierarchy and Levels."""

import logging
from typing import Any

from ml.src.prompts.b5_prompt import get_b5_prompt
from ml.src.schemas.pipeline_steps import HierarchyOutput
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b5_hierarchy(
    learning_units: dict[str, Any],
    time_budget_minutes: int,
    estimated_weeks: int,
    deepseek_client: DeepSeekClient,
) -> tuple[HierarchyOutput, dict[str, Any]]:
    """
    B5: Organize units into hierarchy and levels.

    Args:
        learning_units: Output from B4
        time_budget_minutes: Total time budget
        estimated_weeks: Target weeks
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (hierarchy, metadata)
    """
    logger.info("Starting B5: Hierarchy and levels")

    prompt = get_b5_prompt(learning_units, time_budget_minutes, estimated_weeks)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=HierarchyOutput,
        temperature=0.5,
        max_tokens=3000,
    )

    logger.info(
        f"B5 complete: {len(result.levels)} levels, "
        f"{result.total_weeks} weeks, "
        f"compression={result.time_compression_applied}"
    )

    return result, metadata
