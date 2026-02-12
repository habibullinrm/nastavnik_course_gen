"""B3: KSA Matrix (Knowledge-Skills-Habits)."""

import logging
from typing import Any

from ml.src.prompts.b3_prompt import get_b3_prompt
from ml.src.schemas.pipeline_steps import KSAMatrix
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b3_ksa_matrix(
    profile: dict[str, Any],
    competencies: dict[str, Any],
    deepseek_client: DeepSeekClient,
) -> tuple[KSAMatrix, dict[str, Any]]:
    """
    B3: Decompose competencies into KSA matrix.

    Args:
        profile: Original profile
        competencies: Output from B2
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (KSA matrix, metadata)
    """
    logger.info("Starting B3: KSA matrix decomposition")

    prompt = get_b3_prompt(profile, competencies)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=KSAMatrix,
        temperature=0.7,
        max_tokens=4000,
    )

    logger.info(
        f"B3 complete: K={len(result.knowledge_items)}, "
        f"S={len(result.skill_items)}, H={len(result.habit_items)}"
    )

    return result, metadata
