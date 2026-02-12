"""B1: Profile Validation and Enrichment."""

import json
import logging
from typing import Any

from ml.src.prompts.b1_prompt import get_b1_prompt
from ml.src.schemas.pipeline_steps import ValidatedStudentProfile
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b1_validate(
    profile: dict[str, Any], deepseek_client: DeepSeekClient
) -> tuple[ValidatedStudentProfile, dict[str, Any]]:
    """
    B1: Validate and enrich student profile.

    Args:
        profile: Raw student profile
        deepseek_client: DeepSeek API client

    Returns:
        Tuple of (validated profile, metadata)
    """
    logger.info("Starting B1: Profile validation and enrichment")

    # Generate prompt
    prompt = get_b1_prompt(profile)

    # Call DeepSeek
    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=ValidatedStudentProfile,
        temperature=0.3,  # Lower temperature for validation
        max_tokens=2000,
    )

    logger.info(
        f"B1 complete: effective_level={result.effective_level}, "
        f"estimated_weeks={result.estimated_weeks}"
    )

    return result, metadata
