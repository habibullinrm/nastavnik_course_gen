"""B4: Learning Units Design."""

import logging
from typing import Any

from ml.src.prompts.b4_prompt import get_b4_prompt
from ml.src.schemas.pipeline_steps import LearningUnitsOutput
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b4_learning_units(
    ksa_matrix: dict[str, Any], deepseek_client: DeepSeekClient
) -> tuple[LearningUnitsOutput, dict[str, Any]]:
    """
    B4: Design learning units from KSA items.

    Args:
        ksa_matrix: Output from B3
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (learning units, metadata)
    """
    logger.info("Starting B4: Learning units design")

    prompt = get_b4_prompt(ksa_matrix)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=LearningUnitsOutput,
        temperature=0.7,
        max_tokens=4000,
    )

    logger.info(
        f"B4 complete: {len(result.clusters)} clusters, "
        f"T={len(result.theory_units)}, P={len(result.practice_units)}, "
        f"A={len(result.automation_units)}"
    )

    return result, metadata
