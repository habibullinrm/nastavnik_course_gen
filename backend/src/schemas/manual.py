"""Pydantic schemas for manual debug mode."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Sessions
# ============================================================================


class ManualSessionCreate(BaseModel):
    """Request to create a manual session."""
    profile_id: UUID
    name: str = Field(max_length=255)
    description: str | None = None


class ManualSessionUpdate(BaseModel):
    """Request to update a manual session."""
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    status: str | None = Field(None, pattern=r"^(active|archived)$")
    profile_snapshot: dict[str, Any] | None = None


class ManualSessionResponse(BaseModel):
    """Response for a manual session."""
    id: UUID
    profile_id: UUID
    profile_snapshot: dict[str, Any]
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ManualSessionListResponse(BaseModel):
    """Response for session listing."""
    sessions: list[ManualSessionResponse]
    total: int


# ============================================================================
# Prompt Versions
# ============================================================================


class PromptVersionCreate(BaseModel):
    """Request to create a new prompt version."""
    prompt_text: str
    change_description: str | None = None


class PromptVersionResponse(BaseModel):
    """Response for a prompt version."""
    id: UUID
    step_name: str
    version: int
    prompt_text: str
    change_description: str | None
    is_baseline: bool
    created_at: datetime


class PromptStepSummary(BaseModel):
    """Summary of prompts for a step — latest version info."""
    step_name: str
    latest_version: int
    latest_prompt_id: UUID
    is_baseline: bool
    created_at: datetime


class PromptListResponse(BaseModel):
    """Response for prompt listing (all steps with latest version)."""
    steps: list[PromptStepSummary]


# ============================================================================
# Step Runs
# ============================================================================


class StepRunRequest(BaseModel):
    """Request to run a step."""
    prompt_version_id: UUID | None = None
    custom_prompt: str | None = None
    input_data: dict[str, Any] | None = None
    llm_params: dict[str, Any] | None = None
    run_preprocessors: bool = True
    run_postprocessors: bool = True
    use_mock: bool = True


class StepRunResponse(BaseModel):
    """Response for a step run."""
    id: UUID
    session_id: UUID
    step_name: str
    run_number: int
    prompt_version_id: UUID | None
    rendered_prompt: str | None
    input_data: dict[str, Any] | None
    profile_variables: dict[str, Any] | None
    llm_params: dict[str, Any] | None
    raw_response: str | None
    parsed_result: dict[str, Any] | None
    parse_error: str | None
    tokens_used: int | None
    duration_ms: float | None
    status: str
    preprocessor_results: list[dict[str, Any]] | None
    postprocessor_results: list[dict[str, Any]] | None
    auto_evaluation: dict[str, Any] | None
    llm_judge_evaluation: dict[str, Any] | None
    user_rating: int | None
    user_notes: str | None
    created_at: datetime


class StepRunSummary(BaseModel):
    """Summary of a step run for listing."""
    id: UUID
    run_number: int
    status: str
    duration_ms: float | None
    tokens_used: int | None
    user_rating: int | None
    created_at: datetime


class StepStatusResponse(BaseModel):
    """Status of all steps in a session."""
    steps: dict[str, dict[str, Any]]
    # e.g. {"B1_validate": {"last_run": {...}, "run_count": 3, "status": "completed"}}


class UserRatingUpdate(BaseModel):
    """Request to rate a step run."""
    user_rating: int | None = Field(None, ge=1, le=5)
    user_notes: str | None = None


# ============================================================================
# Processors
# ============================================================================


class ProcessorInfo(BaseModel):
    """Info about an available processor."""
    name: str
    type: str
    applicable_steps: list[str]
    description: str


class ProcessorConfigItem(BaseModel):
    """Config for one processor on a step."""
    processor_name: str
    processor_type: str
    execution_order: int = 0
    enabled: bool = True
    config_params: dict[str, Any] | None = None


class ProcessorConfigUpdate(BaseModel):
    """Request to set processor configs for a step."""
    processors: list[ProcessorConfigItem]


class ProcessorConfigResponse(BaseModel):
    """Response for processor config."""
    step_name: str
    processors: list[ProcessorConfigItem]
