"""Pydantic schemas for CDV (Content Divergence Value) calculation."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CDVCalculateRequest(BaseModel):
    """Request to calculate CDV between track versions."""
    tracks: list[dict[str, Any]]  # List of PersonalizedTrack.track_data
    track_ids: list[UUID]  # Corresponding track IDs


class CDVPair(BaseModel):
    """CDV between two track versions."""
    version_a_id: UUID
    version_b_id: UUID
    cdv_total: float
    cdv_topics: float
    cdv_subtopics: float
    cdv_activities: float


class TopicFrequency(BaseModel):
    """Topic frequency across versions."""
    topic_name: str
    count: int
    total_versions: int
    frequency_pct: float


class CDVCalculateResponse(BaseModel):
    """Response with CDV analysis."""
    cdv_matrix: list[CDVPair]
    topic_frequency: list[TopicFrequency]
    top_stable_topics: list[str]
    top_unstable_topics: list[str]
    mean_cdv: float
    cdv_std: float
    recommendation: str  # "stable" | "needs_improvement" | "unstable"
    generated_at: str  # ISO timestamp
