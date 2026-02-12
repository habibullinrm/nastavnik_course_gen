"""B8: Track Validation."""

import logging
from typing import Any

from ml.src.prompts.b8_prompt import get_b8_prompt
from ml.src.schemas.pipeline_steps import ValidationResult
from ml.src.services.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


async def run_b8_validation(
    complete_track: dict[str, Any],
    profile: dict[str, Any],
    deepseek_client: DeepSeekClient,
    max_retries: int = 3,
) -> tuple[ValidationResult, dict[str, Any]]:
    """
    B8: Validate the complete generated track.

    Performs 22 validation checks and can retry on critical failures.

    Args:
        complete_track: Complete track with all B1-B7 outputs
        profile: Original profile
        deepseek_client: DeepSeek API client
        max_retries: Max retry attempts for critical failures

    Returns:
        Tuple of (validation result, metadata)
    """
    logger.info("Starting B8: Track validation")

    prompt = get_b8_prompt(complete_track, profile)

    result, metadata = await deepseek_client.chat_completion(
        prompt=prompt,
        response_model=ValidationResult,
        temperature=0.3,  # Lower temperature for validation
        max_tokens=3000,
    )

    logger.info(
        f"B8 complete: valid={result.overall_valid}, "
        f"critical={result.critical_failures}, warnings={result.warnings}, "
        f"status={result.final_status}"
    )

    # Note: Retry logic would be implemented in the orchestrator (T040)
    # if result.critical_failures > 0

    return result, metadata
