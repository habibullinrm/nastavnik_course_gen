"""Tests for mock LLM client."""

import pytest

from ml.src.services.mock_llm_client import MockLLMClient


@pytest.fixture
def mock_client():
    """Create mock client instance."""
    return MockLLMClient()


@pytest.mark.asyncio
async def test_mock_client_b1(mock_client):
    """Test mock client returns B1 response."""
    prompt = "You are validating a student profile. Check if all required fields are present..."

    response = await mock_client.complete(prompt)

    assert response["object"] == "chat.completion"
    assert "choices" in response
    assert len(response["choices"]) > 0

    content = response["choices"][0]["message"]["content"]
    assert "validation_status" in content
    assert "effective_level" in content


@pytest.mark.asyncio
async def test_mock_client_b3(mock_client):
    """Test mock client returns B3 response."""
    prompt = "Decompose competencies into a Knowledge-Skills-Habits (KSA) matrix..."

    response = await mock_client.complete(prompt)

    content = response["choices"][0]["message"]["content"]
    assert "knowledge_items" in content
    assert "skill_items" in content
    assert "habit_items" in content


@pytest.mark.asyncio
async def test_mock_client_stats(mock_client):
    """Test mock client tracks statistics."""
    initial_stats = mock_client.get_stats()
    assert initial_stats["call_count"] == 0

    await mock_client.complete("Validate profile...")
    await mock_client.complete("Decompose into KSA...")

    final_stats = mock_client.get_stats()
    assert final_stats["call_count"] == 2
    assert final_stats["total_tokens"] > 0


@pytest.mark.asyncio
async def test_mock_client_unknown_step(mock_client):
    """Test mock client raises error for unknown step."""
    with pytest.raises(ValueError, match="Could not detect step"):
        await mock_client.complete("This is a completely unrelated prompt...")
