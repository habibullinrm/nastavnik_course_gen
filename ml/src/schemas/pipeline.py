"""Pydantic schemas for pipeline operations."""

from typing import Any

from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    """Request to run the pipeline B1-B8."""
    profile: dict[str, Any]
    algorithm_version: str = "v1.0.0"


class StepLog(BaseModel):
    """Log entry for a pipeline step."""
    step_name: str
    duration_sec: float
    tokens_used: int
    success: bool
    error_message: str | None = None


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    algorithm_version: str
    started_at: str
    finished_at: str
    steps_log: list[StepLog]
    llm_calls_count: int
    total_tokens: int
    total_duration_sec: float


class PipelineRunResponse(BaseModel):
    """Response from pipeline run."""
    track_data: dict[str, Any]
    generation_metadata: GenerationMetadata
    validation_b8: dict[str, Any] | None


class PipelineError(BaseModel):
    """Error response from pipeline."""
    error: str
    step: str | None = None
    details: str | None = None
