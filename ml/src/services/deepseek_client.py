"""DeepSeek API client with retry logic and structured output."""

import asyncio
import json
import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from ml.src.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class DeepSeekError(Exception):
    """Base exception for DeepSeek API errors."""
    pass


class DeepSeekRateLimitError(DeepSeekError):
    """Rate limit exceeded."""
    pass


class DeepSeekClient:
    """Async client for DeepSeek API with retry logic."""

    def __init__(self):
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.max_retries = settings.DEEPSEEK_MAX_RETRIES
        self.backoff_base = settings.DEEPSEEK_RETRY_BACKOFF_BASE

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(120.0),  # 2 minutes timeout
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def chat_completion(
        self,
        prompt: str,
        response_model: type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> tuple[T, dict[str, Any]]:
        """
        Make a chat completion request with structured output.

        Args:
            prompt: The prompt to send
            response_model: Pydantic model class for structured response
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (parsed_response, metadata)
            metadata contains: tokens_used, duration_ms, raw_response

        Raises:
            DeepSeekError: On API errors
            ValidationError: If response doesn't match schema
        """
        import time
        start_time = time.time()

        # Build request
        messages = [{"role": "user", "content": prompt}]
        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Retry loop
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"DeepSeek API call attempt {attempt + 1}/{self.max_retries}")

                response = await self.client.post("/chat/completions", json=request_data)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "5"))
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                # Handle server errors
                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}, retrying...")
                    await asyncio.sleep(self.backoff_base ** attempt)
                    continue

                # Check for client errors
                response.raise_for_status()

                # Parse response
                response_json = response.json()
                content = response_json["choices"][0]["message"]["content"]

                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                # Parse as JSON
                try:
                    parsed_json = json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in response: {content[:200]}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.backoff_base ** attempt)
                        continue
                    raise DeepSeekError(f"Invalid JSON in response: {e}")

                # Validate against Pydantic model
                validated_response = response_model.model_validate(parsed_json)

                # Collect metadata
                duration_ms = (time.time() - start_time) * 1000
                tokens_used = response_json.get("usage", {}).get("total_tokens", 0)

                metadata = {
                    "tokens_used": tokens_used,
                    "duration_ms": duration_ms,
                    "raw_response": content,
                    "model": self.model,
                }

                logger.info(
                    f"DeepSeek API success: {tokens_used} tokens, {duration_ms:.0f}ms"
                )

                return validated_response, metadata

            except httpx.TimeoutException as e:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                last_error = DeepSeekError(f"Request timeout: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.backoff_base ** attempt)
                    continue

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                last_error = DeepSeekError(f"HTTP error: {e}")
                if attempt < self.max_retries - 1 and e.response.status_code >= 500:
                    await asyncio.sleep(self.backoff_base ** attempt)
                    continue
                break  # Don't retry client errors

            except ValidationError as e:
                logger.error(f"Response validation error: {e}")
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.backoff_base ** attempt)
                    continue

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                last_error = DeepSeekError(f"Unexpected error: {e}")
                break

        # All retries exhausted
        raise last_error or DeepSeekError("All retry attempts failed")


# Global client instance
_client: DeepSeekClient | None = None


async def get_deepseek_client() -> DeepSeekClient:
    """Get or create global DeepSeek client instance."""
    global _client
    if _client is None:
        _client = DeepSeekClient()
    return _client


async def close_deepseek_client():
    """Close global DeepSeek client."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
