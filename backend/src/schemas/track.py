"""Pydantic schemas for personalized tracks."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class GenerationStartedResponse(BaseModel):
    """Response when track generation starts."""
    track_id: UUID
    status: str
    progress_url: str


class TrackSummary(BaseModel):
    """Summary info for track listing."""
    id: UUID
    profile_id: UUID
    topic: str | None = None  # Extracted from track_data
    algorithm_version: str
    status: str
    generation_duration_sec: float | None
    created_at: datetime


class TrackDetail(BaseModel):
    """Detailed track info with full data."""
    id: UUID
    profile_id: UUID
    qa_report_id: UUID | None
    track_data: dict[str, Any]
    generation_metadata: dict[str, Any]
    algorithm_version: str
    validation_b8: dict[str, Any] | None
    status: str
    error_message: str | None
    generation_duration_sec: float | None
    batch_index: int | None
    created_at: datetime
    updated_at: datetime


class TrackListResponse(BaseModel):
    """Response for track listing."""
    tracks: list[TrackSummary]
    total: int


class FieldUsageItem(BaseModel):
    """Field usage information."""
    field_name: str
    used: bool
    steps: list[str] = Field(default_factory=list)  # Which steps used this field


class FieldUsageResponse(BaseModel):
    """Response for field usage analysis."""
    track_id: UUID
    used_fields: list[FieldUsageItem]
    unused_fields: list[str]
