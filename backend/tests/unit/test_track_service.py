"""
Тесты для track_service: background task, cancel, batch.

Используют моки — не требуют БД или ML сервис.
"""

import asyncio
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.src.schemas.track import (
    GenerationStartedResponse,
    BatchGenerationStartedResponse,
    TrackDetail,
)


@pytest.fixture
def mock_db():
    """Mock AsyncSession."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def mock_profile():
    """Mock StudentProfile ORM object."""
    profile = MagicMock()
    profile.id = uuid.uuid4()
    profile.data = {
        "topic": "Python",
        "experience_level": "beginner",
    }
    return profile


@pytest.fixture
def mock_track():
    """Mock PersonalizedTrack ORM object."""
    track = MagicMock()
    track.id = uuid.uuid4()
    track.profile_id = uuid.uuid4()
    track.track_data = {}
    track.generation_metadata = {}
    track.algorithm_version = "v1.0"
    track.validation_b8 = None
    track.status = "pending"
    track.error_message = None
    track.generation_duration_sec = None
    track.batch_id = None
    track.batch_index = None
    track.created_at = datetime.utcnow()
    track.updated_at = datetime.utcnow()
    return track


class TestGenerateTrack:
    """Тесты generate_track — создаёт трек и запускает background task."""

    @patch("backend.src.services.track_service._run_generation", new_callable=AsyncMock)
    async def test_generate_track_returns_202_immediately(
        self, mock_run, mock_db, mock_profile
    ):
        """generate_track возвращает GenerationStartedResponse сразу, не ждёт ML."""
        from backend.src.services.track_service import generate_track

        # Mock DB: profile exists
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_profile
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await generate_track(mock_profile.id, mock_db)

        assert isinstance(result, GenerationStartedResponse)
        assert result.status == "pending"
        assert "/progress" in result.progress_url

    async def test_generate_track_raises_for_missing_profile(self, mock_db):
        """generate_track бросает ValueError если профиль не найден."""
        from backend.src.services.track_service import generate_track

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="not found"):
            await generate_track(uuid.uuid4(), mock_db)


class TestCancelTrack:
    """Тесты cancel_track — остановка генерации."""

    async def test_cancel_running_track(self, mock_db, mock_track):
        """cancel_track ставит статус cancelling для running трека."""
        from backend.src.services.track_service import cancel_track

        mock_track.status = "running"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_track
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await cancel_track(mock_track.id, mock_db)

        assert result is True
        assert mock_track.status == "cancelling"

    async def test_cancel_pending_track(self, mock_db, mock_track):
        """cancel_track работает и для pending трека."""
        from backend.src.services.track_service import cancel_track

        mock_track.status = "pending"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_track
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await cancel_track(mock_track.id, mock_db)

        assert result is True
        assert mock_track.status == "cancelling"

    async def test_cancel_completed_track_raises(self, mock_db, mock_track):
        """cancel_track бросает ValueError для уже завершённого трека."""
        from backend.src.services.track_service import cancel_track

        mock_track.status = "completed"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_track
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Cannot cancel"):
            await cancel_track(mock_track.id, mock_db)

    async def test_cancel_nonexistent_track_raises(self, mock_db):
        """cancel_track бросает ValueError если трек не найден."""
        from backend.src.services.track_service import cancel_track

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="not found"):
            await cancel_track(uuid.uuid4(), mock_db)


class TestGenerateTrackBatch:
    """Тесты generate_track_batch — batch-генерация."""

    @patch("backend.src.services.track_service._run_batch_generation", new_callable=AsyncMock)
    async def test_batch_creates_n_tracks(self, mock_run, mock_db, mock_profile):
        """generate_track_batch создаёт N треков с общим batch_id."""
        from backend.src.services.track_service import generate_track_batch

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_profile
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await generate_track_batch(mock_profile.id, 3, mock_db)

        assert isinstance(result, BatchGenerationStartedResponse)
        assert len(result.track_ids) == 3
        assert result.status == "pending"
        assert "batch" in result.progress_url

    @patch("backend.src.services.track_service._run_batch_generation", new_callable=AsyncMock)
    async def test_batch_raises_for_missing_profile(self, mock_run, mock_db):
        """generate_track_batch бросает ValueError если профиль не найден."""
        from backend.src.services.track_service import generate_track_batch

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="not found"):
            await generate_track_batch(uuid.uuid4(), 3, mock_db)


class TestTrackAPIHelpers:
    """Тесты вспомогательных функций из tracks.py."""

    def test_step_summary_b1(self):
        """_step_summary извлекает метрики B1."""
        from backend.src.api.tracks import _step_summary

        summary = _step_summary("B1_validate", {
            "effective_level": "intermediate",
            "estimated_weeks": 8,
        })
        assert summary["effective_level"] == "intermediate"
        assert summary["estimated_weeks"] == 8

    def test_step_summary_b2(self):
        """_step_summary считает competencies для B2."""
        from backend.src.api.tracks import _step_summary

        summary = _step_summary("B2_competencies", {
            "competencies": [{"id": 1}, {"id": 2}, {"id": 3}],
        })
        assert summary["competencies_count"] == 3

    def test_step_summary_b4(self):
        """_step_summary считает units и clusters для B4."""
        from backend.src.api.tracks import _step_summary

        summary = _step_summary("B4_learning_units", {
            "units": [1, 2, 3, 4],
            "clusters": [1, 2],
        })
        assert summary["units_count"] == 4
        assert summary["clusters_count"] == 2

    def test_step_summary_b8(self):
        """_step_summary извлекает overall_valid для B8."""
        from backend.src.api.tracks import _step_summary

        summary = _step_summary("B8_validation", {
            "overall_valid": True,
            "checks": [{"name": "c1"}, {"name": "c2"}],
        })
        assert summary["overall_valid"] is True
        assert summary["checks"] == 2

    def test_make_sse_format(self):
        """_make_sse форматирует SSE event корректно."""
        from backend.src.api.tracks import _make_sse

        result = _make_sse("step_update", {"step": "B1", "status": "running"})
        assert result.startswith("event: step_update\n")
        assert '"step": "B1"' in result
        assert result.endswith("\n\n")


class TestSchemas:
    """Тесты Pydantic schemas."""

    def test_generate_batch_request_validation(self):
        """GenerateBatchRequest валидирует batch_size 2-5."""
        from backend.src.schemas.track import GenerateBatchRequest

        # Valid
        req = GenerateBatchRequest(profile_id=uuid.uuid4(), batch_size=3)
        assert req.batch_size == 3

        # Too small
        with pytest.raises(Exception):
            GenerateBatchRequest(profile_id=uuid.uuid4(), batch_size=1)

        # Too large
        with pytest.raises(Exception):
            GenerateBatchRequest(profile_id=uuid.uuid4(), batch_size=6)

    def test_batch_generation_started_response(self):
        """BatchGenerationStartedResponse сериализуется корректно."""
        from backend.src.schemas.track import BatchGenerationStartedResponse

        batch_id = uuid.uuid4()
        track_ids = [uuid.uuid4() for _ in range(3)]

        resp = BatchGenerationStartedResponse(
            batch_id=batch_id,
            track_ids=track_ids,
            status="pending",
            progress_url=f"/api/tracks/batch/{batch_id}/progress",
        )
        data = resp.model_dump()
        assert len(data["track_ids"]) == 3
        assert data["status"] == "pending"

    def test_track_detail_has_batch_fields(self):
        """TrackDetail содержит batch_id и batch_index."""
        from backend.src.schemas.track import TrackDetail

        detail = TrackDetail(
            id=uuid.uuid4(),
            profile_id=uuid.uuid4(),
            track_data={},
            generation_metadata={},
            algorithm_version="v1.0",
            status="completed",
            batch_id=uuid.uuid4(),
            batch_index=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert detail.batch_id is not None
        assert detail.batch_index == 0
