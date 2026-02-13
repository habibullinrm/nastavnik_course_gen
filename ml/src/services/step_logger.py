"""Service for logging pipeline step results to backend."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)


class StepLogger:
    """Logger for pipeline steps - saves to backend and optionally to files."""

    def __init__(self, backend_url: str = "http://backend:8000"):
        self.backend_url = backend_url
        self.disable_backend = os.getenv("DISABLE_BACKEND_LOGGING", "false").lower() == "true"
        self.client = httpx.AsyncClient(base_url=backend_url, timeout=30.0) if not self.disable_backend else None

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()

    async def log_step(
        self,
        track_id: UUID,
        step_name: str,
        step_output: dict[str, Any],
        llm_calls: list[dict[str, Any]],
        duration_sec: float,
        error_message: str | None = None,
        save_to_file: bool = True,
    ) -> bool:
        """
        Log a pipeline step result.

        Args:
            track_id: ID of the track being generated
            step_name: Name of the step (B1_validate, B2_competencies, etc.)
            step_output: The output data from the step
            llm_calls: List of LLM calls made during this step
            duration_sec: Duration of the step in seconds
            error_message: Optional error message if step failed
            save_to_file: Whether to also save to local file

        Returns:
            True if successfully logged
        """
        # Prepare log data
        log_data = {
            "track_id": str(track_id),
            "step_name": step_name,
            "step_output": step_output,
            "llm_calls": llm_calls,
            "step_duration_sec": duration_sec,
            "error_message": error_message,
        }

        # Try to send to backend (unless disabled)
        if not self.disable_backend:
            try:
                response = await self.client.post("/api/logs/step", json=log_data)
                response.raise_for_status()
                logger.info(f"Successfully logged step {step_name} for track {track_id}")
            except Exception as e:
                logger.error(f"Failed to log step {step_name} to backend: {e}")
                # Continue anyway - file logging might still work
        else:
            logger.debug(f"Backend logging disabled, skipping step {step_name}")

        # Optionally save to file
        if save_to_file:
            try:
                log_dir = Path("ml/logs") / str(track_id)
                log_dir.mkdir(parents=True, exist_ok=True)

                log_file = log_dir / f"step_{step_name}.json"
                with open(log_file, "w", encoding="utf-8") as f:
                    json.dump(log_data, f, indent=2, ensure_ascii=False)

                logger.info(f"Saved step log to {log_file}")
            except Exception as e:
                logger.error(f"Failed to save step log to file: {e}")

        return True


# Global logger instance
_step_logger: StepLogger | None = None


async def get_step_logger() -> StepLogger:
    """Get or create global step logger instance."""
    global _step_logger
    if _step_logger is None:
        _step_logger = StepLogger()
    return _step_logger


async def close_step_logger():
    """Close global step logger."""
    global _step_logger
    if _step_logger is not None:
        await _step_logger.close()
        _step_logger = None
