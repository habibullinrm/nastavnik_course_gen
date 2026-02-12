"""B7: Schedule Assembly."""

import logging
from typing import Any

from ml.src.prompts.b7_prompt import get_b7_prompt
from ml.src.schemas.pipeline_steps import ScheduleOutput
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b7_schedule(
    hierarchy: dict[str, Any],
    blueprints: dict[str, Any],
    profile: dict[str, Any],
    total_weeks: int,
    deepseek_client: DeepSeekClient,
) -> tuple[ScheduleOutput, dict[str, Any]]:
    """
    B7: Assemble weekly schedule with daily distribution.

    Args:
        hierarchy: Output from B5
        blueprints: Output from B6
        profile: Original profile (for schedule/availability)
        total_weeks: Target weeks
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (schedule, metadata)
    """
    logger.info("Starting B7: Schedule assembly")

    # Extract schedule info from profile
    schedule_info = {
        "schedule": profile.get("schedule", []),
        "practice_windows": profile.get("practice_windows", []),
        "weekly_hours": profile.get("weekly_hours", 5),
    }

    prompt = get_b7_prompt(hierarchy, blueprints, schedule_info, total_weeks)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=ScheduleOutput,
        temperature=0.6,
        max_tokens=4000,
    )

    logger.info(
        f"B7 complete: {result.total_weeks} weeks, "
        f"{len(result.checkpoints)} checkpoints"
    )

    return result, metadata
