"""Pydantic schemas for QA reports."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CDVPair(BaseModel):
    """CDV (Content Divergence Value) between two track versions."""
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


class BatchStartedResponse(BaseModel):
    """Response when batch generation starts."""
    report_id: UUID
    profile_id: UUID
    batch_size: int
    status: str
    progress_url: str


class QAReportSummary(BaseModel):
    """Summary info for QA report listing."""
    id: UUID
    profile_id: UUID
    batch_size: int
    completed_count: int
    mean_cdv: float | None
    recommendation: str | None
    status: str
    created_at: datetime


class QAReportDetail(BaseModel):
    """Detailed QA report with full analysis."""
    id: UUID
    profile_id: UUID
    report_data: dict | None
    batch_size: int
    completed_count: int
    mean_cdv: float | None
    cdv_std: float | None
    recommendation: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class QAReportListResponse(BaseModel):
    """Response for QA report listing."""
    reports: list[QAReportSummary]
    total: int
