"""Mock LLM client for testing pipeline without real API calls."""

import json
import logging
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class MockLLMClient:
    """Mock LLM client that returns predefined responses for each step."""

    def __init__(
        self,
        fixtures_dir: str = "tests/fixtures/mock_responses",
        fixed_step_name: str | None = None,
    ):
        """
        Initialize mock client.

        Args:
            fixtures_dir: Directory with mock JSON responses for B1-B8
            fixed_step_name: If set, always use this step instead of auto-detection
        """
        self.fixtures_dir = Path(fixtures_dir)
        self.call_count = 0
        self.total_tokens = 0
        self.fixed_step_name = fixed_step_name

        # Load all fixtures
        self.fixtures = {}
        for step_file in self.fixtures_dir.glob("*.json"):
            step_name = step_file.stem  # B1_validate, B2_competencies, etc.
            with open(step_file, encoding="utf-8") as f:
                self.fixtures[step_name] = json.load(f)

        logger.info(f"MockLLMClient initialized with {len(self.fixtures)} fixtures")

    async def complete(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Mock completion - returns predefined response based on prompt content.

        Args:
            prompt: The prompt (analyzed to detect which step it is)
            model: Model name (ignored in mock)
            temperature: Temperature (ignored in mock)
            max_tokens: Max tokens (ignored in mock)

        Returns:
            Mock response matching OpenAI API format
        """
        # Detect which step based on prompt content
        step_name = self._detect_step(prompt)

        if step_name not in self.fixtures:
            raise ValueError(
                f"No mock fixture found for step {step_name}. "
                f"Available: {list(self.fixtures.keys())}"
            )

        response_data = self.fixtures[step_name]

        # Simulate token usage
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(json.dumps(response_data).split()) * 1.3
        total_tokens = int(input_tokens + output_tokens)

        self.call_count += 1
        self.total_tokens += total_tokens

        logger.info(
            f"MockLLM: Returning {step_name} response "
            f"(call #{self.call_count}, ~{total_tokens} tokens)"
        )

        # Return in OpenAI API format
        return {
            "id": f"mock-{self.call_count}",
            "object": "chat.completion",
            "created": 1234567890,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(response_data, ensure_ascii=False),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": int(input_tokens),
                "completion_tokens": int(output_tokens),
                "total_tokens": total_tokens,
            },
        }

    async def chat_completion(
        self,
        prompt: str,
        response_model: type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        step_name: str | None = None,
    ) -> tuple[T, dict[str, Any]]:
        """
        Mock chat completion with structured output (compatible with DeepSeekClient).

        Args:
            prompt: The prompt to send
            response_model: Pydantic model class for structured response
            temperature: Sampling temperature (ignored in mock)
            max_tokens: Maximum tokens in response (ignored in mock)
            step_name: Explicit step name (e.g., 'B1_validate') - if None, will auto-detect

        Returns:
            Tuple of (parsed_response, metadata)
        """
        import time
        start_time = time.time()

        # Priority: parameter > fixed_step_name > auto-detect
        if step_name is None:
            step_name = self.fixed_step_name
        if step_name is None:
            step_name = self._detect_step(prompt)

        if step_name not in self.fixtures:
            raise ValueError(
                f"No mock fixture found for step {step_name}. "
                f"Available: {list(self.fixtures.keys())}"
            )

        response_data = self.fixtures[step_name]

        # Validate against Pydantic model
        validated_response = response_model.model_validate(response_data)

        # Simulate token usage
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(json.dumps(response_data).split()) * 1.3
        total_tokens = int(input_tokens + output_tokens)

        self.call_count += 1
        self.total_tokens += total_tokens

        # Collect metadata (matching DeepSeekClient format)
        duration_ms = (time.time() - start_time) * 1000
        metadata = {
            "tokens_used": total_tokens,
            "duration_ms": duration_ms,
            "raw_response": json.dumps(response_data, ensure_ascii=False),
            "model": "mock-llm",
        }

        logger.info(
            f"MockLLM: Returning {step_name} response "
            f"(call #{self.call_count}, ~{total_tokens} tokens, {duration_ms:.1f}ms)"
        )

        return validated_response, metadata

    def _detect_step(self, prompt: str) -> str:
        """
        Detect which pipeline step based on prompt keywords.

        Args:
            prompt: The prompt text

        Returns:
            Step name (e.g., "B1_validate")
        """
        prompt_lower = prompt.lower()

        # Detection rules based on prompt content (order matters - more specific first)

        # B8: validation of complete track (must be specific to avoid false positives)
        if (("validation" in prompt_lower or "validate" in prompt_lower) and
            "complete track" in prompt_lower):
            return "B8_validation"

        # B2: competencies formulation (check before B1 as it may contain "validated profile")
        if "competenc" in prompt_lower and "formulate" in prompt_lower:
            return "B2_competencies"

        # B5: hierarchy (check early as it may contain "learning units")
        if "hierarchy" in prompt_lower or "leveled" in prompt_lower or "topological" in prompt_lower:
            return "B5_hierarchy"

        # B6: problem formulations / blueprints (check before B4 as it may contain "units")
        if "problem formulation" in prompt_lower or "blueprints" in prompt_lower or "pbl" in prompt_lower:
            return "B6_problem_formulations"

        # B7: schedule assembly (check before B4 as it may contain "units")
        if "schedule" in prompt_lower or "weekly" in prompt_lower or "calendar" in prompt_lower:
            return "B7_schedule"

        # B4: learning units (check before B3 as B4 prompt contains "KSA MATRIX" reference)
        if "learning units" in prompt_lower or "theory units" in prompt_lower or "practice units" in prompt_lower:
            return "B4_learning_units"

        # B3: KSA matrix (check before B1 as it may mention profile)
        if "ksa" in prompt_lower or "knowledge-skills-habits" in prompt_lower or ("decompose" in prompt_lower and "competenc" in prompt_lower):
            return "B3_ksa_matrix"

        # B1: validation of student profile
        if ("validat" in prompt_lower and "profile" in prompt_lower) or ("enrich" in prompt_lower and "profile" in prompt_lower):
            return "B1_validate"

        # Fallback: could not detect
        raise ValueError(
            f"Could not detect step from prompt. "
            f"Prompt starts with: {prompt[:200]}..."
        )

    def get_stats(self) -> dict[str, Any]:
        """Get mock client statistics."""
        return {
            "call_count": self.call_count,
            "total_tokens": self.total_tokens,
            "avg_tokens_per_call": (
                self.total_tokens / self.call_count if self.call_count > 0 else 0
            ),
        }


# Global mock client instance
_mock_client: MockLLMClient | None = None


def get_mock_client() -> MockLLMClient:
    """Get or create global mock client."""
    global _mock_client
    if _mock_client is None:
        _mock_client = MockLLMClient()
    return _mock_client
