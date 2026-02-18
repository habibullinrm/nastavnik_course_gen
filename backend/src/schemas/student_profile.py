"""Pydantic schemas for student profiles."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Student Profile Input Structures (from phase_a.md)
class Task(BaseModel):
    """Task structure."""
    id: str
    description: str
    complexity_rank: int


class Subtask(BaseModel):
    """Subtask structure."""
    id: str
    description: str
    parent_task_id: str
    required_knowledge: list[str]
    required_skills: list[str]


class Barrier(BaseModel):
    """Learning barrier structure."""
    id: str
    description: str
    related_task_id: str
    barrier_type: str


class Concept(BaseModel):
    """Confusing concept structure."""
    id: str
    term: str
    confusion_description: str


class Criterion(BaseModel):
    """Success criterion structure."""
    id: str
    description: str
    measurable: bool
    metric: str | None = None


class ScheduleDay(BaseModel):
    """Weekly schedule day."""
    day_of_week: str
    available_minutes: int


class PracticeWindow(BaseModel):
    """Practice window structure."""
    time_of_day: str
    duration_minutes: int
    device: str


class StudentProfileInput(BaseModel):
    """Full student profile input from Phase A (for validation)."""

    # CRITICAL fields
    topic: str
    subject_area: str
    experience_level: Literal["zero", "beginner", "intermediate", "advanced"]
    desired_outcomes: list[str]
    target_tasks: list[Task]
    task_hierarchy: list[Task]
    peak_task_id: str
    easiest_task_id: str | None = None
    subtasks: list[Subtask]
    key_barriers: list[Barrier] | None = None
    confusing_concepts: list[Concept]
    diagnostic_result: Literal["mastery", "partial", "gaps", "misconceptions", "zero"] = Field(
        ..., description="Canonical field name (maps to diagnostic_level in phase_b)"
    )
    weekly_hours: int
    success_criteria: list[Criterion]

    # IMPORTANT fields (optional with warnings)
    schedule: list[ScheduleDay] | None = None
    practice_windows: list[PracticeWindow] | None = None
    preferred_formats: list[str] | None = None
    tech_access: list[str] | None = None
    motivation_level: str | None = None
    support_available: list[str] | None = None
    deadline: str | None = None

    # OPTIONAL fields
    age_group: str | None = None
    learning_style: list[str] | None = None
    prior_attempts: str | None = None
    external_resources: list[str] | None = None
    notes: str | None = None


class ValidationResult(BaseModel):
    """Validation result for uploaded profile."""
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ProfileUploadResponse(BaseModel):
    """Response after uploading profile."""
    id: UUID
    filename: str
    topic: str
    experience_level: str | None
    validation_result: ValidationResult
    created_at: datetime


class ProfileSummary(BaseModel):
    """Summary info for profile listing."""
    id: UUID
    filename: str
    topic: str
    profile_name: str | None = None
    experience_level: str | None
    created_at: datetime


class ProfileDetail(BaseModel):
    """Detailed profile info."""
    id: UUID
    filename: str
    topic: str
    experience_level: str | None
    data: dict[str, Any]
    validation_result: ValidationResult
    created_at: datetime
    updated_at: datetime


class ProfileFormResponse(BaseModel):
    """Ответ после создания или обновления профиля через форму."""
    id: UUID
    topic: str
    experience_level: str | None
    validation_result: ValidationResult
    created_at: datetime
    updated_at: datetime | None = None
