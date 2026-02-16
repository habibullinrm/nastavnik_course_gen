"""
Тесты для pipeline_orchestrator: cancellation, batch, PipelineCancelled.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from ml.src.services.pipeline_orchestrator import (
    PipelineCancelled,
    PipelineError,
    _check_cancelled,
)
from ml.src.schemas.pipeline import (
    PipelineBatchRequest,
    PipelineBatchResponse,
    StepLog,
)


class TestPipelineCancelled:
    """Тесты PipelineCancelled exception."""

    def test_pipeline_cancelled_stores_steps(self):
        exc = PipelineCancelled(["B1", "B2", "B3"])
        assert exc.completed_steps == ["B1", "B2", "B3"]
        assert "B1, B2, B3" in str(exc)

    def test_pipeline_cancelled_empty_steps(self):
        exc = PipelineCancelled([])
        assert exc.completed_steps == []


class TestCheckCancelled:
    """Тесты _check_cancelled — проверка статуса через backend."""

    async def test_check_cancelled_returns_true_for_cancelling(self, respx_or_manual):
        """Если статус cancelling — возвращает True."""
        mock_response = httpx.Response(200, json={"status": "cancelling"})

        with patch("ml.src.services.pipeline_orchestrator.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = instance
            # Make it work as async context manager
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)

            result = await _check_cancelled(uuid.uuid4())
            assert result is True

    async def test_check_cancelled_returns_false_for_running(self):
        """Если статус running — возвращает False."""
        mock_response = httpx.Response(200, json={"status": "running"})

        with patch("ml.src.services.pipeline_orchestrator.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = instance
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)

            result = await _check_cancelled(uuid.uuid4())
            assert result is False

    async def test_check_cancelled_returns_false_on_network_error(self):
        """При ошибке сети — возвращает False (не блокирует pipeline)."""
        with patch("ml.src.services.pipeline_orchestrator.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            mock_cls.return_value = instance
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)

            result = await _check_cancelled(uuid.uuid4())
            assert result is False

    async def test_check_cancelled_returns_true_for_cancelled_status(self):
        """Если статус cancelled (уже) — тоже возвращает True."""
        mock_response = httpx.Response(200, json={"status": "cancelled"})

        with patch("ml.src.services.pipeline_orchestrator.httpx.AsyncClient") as mock_cls:
            instance = AsyncMock()
            instance.get = AsyncMock(return_value=mock_response)
            mock_cls.return_value = instance
            instance.__aenter__ = AsyncMock(return_value=instance)
            instance.__aexit__ = AsyncMock(return_value=False)

            result = await _check_cancelled(uuid.uuid4())
            assert result is True


class TestBatchSchemas:
    """Тесты Pydantic schemas для batch."""

    def test_batch_request_schema(self):
        req = PipelineBatchRequest(
            profile={"topic": "Python"},
            track_ids=["abc-123", "def-456"],
            algorithm_version="v1.0",
        )
        assert len(req.track_ids) == 2

    def test_batch_response_schema(self):
        resp = PipelineBatchResponse(
            results=[
                {"track_data": {}, "status": "completed"},
                {"status": "cancelled", "completed_steps": ["B1"]},
            ]
        )
        assert len(resp.results) == 2
        assert resp.results[1]["status"] == "cancelled"


class TestPipelineError:
    """Тесты PipelineError."""

    def test_pipeline_error_attrs(self):
        exc = PipelineError("B3_ksa_matrix", "LLM timeout", details={"retry": 3})
        assert exc.step == "B3_ksa_matrix"
        assert exc.message == "LLM timeout"
        assert exc.details == {"retry": 3}
        assert "B3_ksa_matrix" in str(exc)


# Фикстура-заглушка для respx (если не установлен)
@pytest.fixture
def respx_or_manual():
    """Placeholder fixture."""
    yield
