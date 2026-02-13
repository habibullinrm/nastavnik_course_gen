"""Factory for LLM clients - supports real and mock modes."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


async def get_llm_client(mock_mode: bool | None = None) -> Any:
    """
    Get LLM client (real DeepSeek or mock).

    Args:
        mock_mode: Force mock mode (True) or real mode (False).
                   If None, reads from MOCK_LLM environment variable.

    Returns:
        DeepSeekClient or MockLLMClient instance
    """
    # Determine mode
    if mock_mode is None:
        mock_mode = os.getenv("MOCK_LLM", "false").lower() in ("true", "1", "yes")

    if mock_mode:
        logger.info("🎭 Using MockLLMClient (no real API calls)")
        from ml.src.services.mock_llm_client import get_mock_client

        return get_mock_client()
    else:
        logger.info("🌐 Using DeepSeekClient (real API calls)")
        from ml.src.services.deepseek_client import get_deepseek_client

        return await get_deepseek_client()


def is_mock_mode() -> bool:
    """Check if mock mode is enabled via environment variable."""
    return os.getenv("MOCK_LLM", "false").lower() in ("true", "1", "yes")
