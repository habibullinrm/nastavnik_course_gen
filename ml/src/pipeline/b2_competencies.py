"""B2: Competency Formulation."""

import logging
from typing import Any

from ml.src.prompts.b2_prompt import get_b2_prompt
from ml.src.schemas.pipeline_steps import CompetencySet
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b2_competencies(
    validated_profile: dict[str, Any], deepseek_client: DeepSeekClient
) -> tuple[CompetencySet, dict[str, Any]]:
    """
    B2: Formulate competencies from tasks and outcomes.

    Args:
        validated_profile: Output from B1
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (competency set, metadata)
    """
    logger.info("Starting B2: Competency formulation")

    # Generate prompt
    prompt = get_b2_prompt(validated_profile)

    # Call DeepSeek
    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=CompetencySet,
        temperature=0.7,
        max_tokens=3000,
    )

    logger.info(
        f"B2 complete: {len(result.competencies)} competencies formulated, "
        f"integral: {result.integral_competency_id}"
    )

    return result, metadata
