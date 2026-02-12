"""Pydantic schemas for intermediate pipeline results (B1-B8)."""

from typing import Literal
from pydantic import BaseModel, Field


# ============================================================================
# B1: Validated Student Profile
# ============================================================================

class ValidatedStudentProfile(BaseModel):
    """Output of B1: validated and enriched profile."""
    # Original profile data (all fields from input)
    original_profile: dict

    # Validation status
    validation_status: Literal["valid", "valid_with_warnings", "invalid"]
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)

    # Enriched fields (system-generated)
    effective_level: Literal["zero", "beginner", "intermediate", "advanced"]
    estimated_weeks: int
    weekly_time_budget_minutes: int
    total_time_budget_minutes: int

    class Config:
        json_schema_extra = {
            "example": {
                "validation_status": "valid",
                "effective_level": "beginner",
                "estimated_weeks": 12,
                "weekly_time_budget_minutes": 300,
                "total_time_budget_minutes": 3600,
            }
        }


# ============================================================================
# B2: Competency Set
# ============================================================================

class Competency(BaseModel):
    """A single competency."""
    id: str
    title: str
    description: str
    related_task_ids: list[str]
    related_outcome_indices: list[int]
    level: Literal["foundational", "intermediate", "advanced", "integrative"]


class CompetencySet(BaseModel):
    """Output of B2: formulated competencies."""
    competencies: list[Competency]
    integral_competency_id: str  # ID of the peak/integrative competency
    competency_task_map: dict[str, list[str]]  # competency_id -> task_ids
    competency_outcome_map: dict[str, list[int]]  # competency_id -> outcome_indices


# ============================================================================
# B3: KSA Matrix (Knowledge, Skills, Habits)
# ============================================================================

class KnowledgeItem(BaseModel):
    """Knowledge item (Знание)."""
    id: str
    title: str
    description: str
    source: str  # e.g., "confusing_concept:c1", "barrier:b2", "gap:implicit"
    required_for: list[str]  # skill/habit IDs


class SkillItem(BaseModel):
    """Skill item (Умение)."""
    id: str
    title: str
    description: str
    source: str  # e.g., "subtask:st1"
    requires_knowledge: list[str]  # knowledge IDs
    required_for: list[str]  # habit IDs


class HabitItem(BaseModel):
    """Habit item (Навык - automated practice)."""
    id: str
    title: str
    description: str
    source: str  # e.g., "mastery_signal:ms1"
    requires_skills: list[str]  # skill IDs


class DependencyEdge(BaseModel):
    """Dependency between KSA items."""
    from_id: str
    to_id: str
    dependency_type: Literal["prerequisite", "supports", "enables"]


class KSAMatrix(BaseModel):
    """Output of B3: Knowledge-Skills-Habits matrix with dependencies."""
    knowledge_items: list[KnowledgeItem]
    skill_items: list[SkillItem]
    habit_items: list[HabitItem]
    dependency_graph: list[DependencyEdge]


# ============================================================================
# B4: Learning Units
# ============================================================================

class TheoryUnit(BaseModel):
    """Theory learning unit."""
    id: str
    title: str
    knowledge_ids: list[str]
    estimated_minutes: int
    content_outline: str


class PracticeUnit(BaseModel):
    """Practice learning unit."""
    id: str
    title: str
    skill_ids: list[str]
    estimated_minutes: int
    exercises_outline: str


class AutomationUnit(BaseModel):
    """Automation/habit learning unit."""
    id: str
    title: str
    habit_ids: list[str]
    estimated_minutes: int
    practice_outline: str


class LearningUnitCluster(BaseModel):
    """Cluster of related learning units (4C/ID whole task)."""
    id: str
    title: str
    theory_units: list[str]  # IDs
    practice_units: list[str]  # IDs
    automation_units: list[str]  # IDs
    total_minutes: int


class LearningUnitsOutput(BaseModel):
    """Output of B4: designed learning units and clusters."""
    theory_units: list[TheoryUnit]
    practice_units: list[PracticeUnit]
    automation_units: list[AutomationUnit]
    clusters: list[LearningUnitCluster]


# ============================================================================
# B5: Hierarchy and Levels
# ============================================================================

class TrackLevel(BaseModel):
    """A level in the track hierarchy."""
    level: Literal["foundational", "intermediate", "advanced", "integrative"]
    clusters: list[str]  # cluster IDs
    estimated_weeks: int


class HierarchyOutput(BaseModel):
    """Output of B5: leveled hierarchy and sequencing."""
    levels: list[TrackLevel]
    unit_sequence: list[str]  # Ordered list of all unit IDs (topological sort)
    time_compression_applied: bool
    total_weeks: int


# ============================================================================
# B6: Lesson Blueprints (Problem Formulations)
# ============================================================================

class ProblemFormulation(BaseModel):
    """Problem formulation for a cluster."""
    problem_statement: str
    expected_hypotheses: list[str]


class LessonBlueprint(BaseModel):
    """Lesson blueprint with PBL components."""
    id: str
    cluster_id: str
    problem_formulation: ProblemFormulation
    knowledge_infusions: list[str]  # КИ-порции
    practice_tasks: list[str]  # Задания на ПМ
    contradictions: list[str]  # Противоречия для исследования
    synthesis_tasks: list[str]  # Задания на синтез
    reflection_questions: list[str]
    fsm_rules: dict  # Finite State Machine rules for adaptive flow


class BlueprintsOutput(BaseModel):
    """Output of B6: lesson blueprints."""
    blueprints: list[LessonBlueprint]


# ============================================================================
# B7: Schedule Assembly
# ============================================================================

class TrackDay(BaseModel):
    """A single day in the schedule."""
    day_of_week: str
    learning_units: list[str]  # Unit IDs for this day
    total_minutes: int


class Checkpoint(BaseModel):
    """A checkpoint for self-assessment."""
    week_number: int
    title: str
    assessment_tasks: list[str]


class TrackWeek(BaseModel):
    """A week in the track."""
    week_number: int
    level: str
    theme: str
    weekly_goals: list[str]
    days: list[TrackDay]
    checkpoint: Checkpoint | None


class SupportPlan(BaseModel):
    """Support mechanisms."""
    scaffolding_techniques: list[str]
    feedback_points: list[str]
    resources: list[str]


class Milestone(BaseModel):
    """Progress milestone."""
    week: int
    title: str
    criteria: list[str]


class ScheduleOutput(BaseModel):
    """Output of B7: assembled weekly schedule."""
    weeks: list[TrackWeek]
    total_weeks: int
    checkpoints: list[Checkpoint]
    final_assessment: dict
    support_plan: SupportPlan
    progress_milestones: list[Milestone]


# ============================================================================
# B8: Validation Result
# ============================================================================

class ValidationCheck(BaseModel):
    """Single validation check."""
    check_name: str
    passed: bool
    severity: Literal["critical", "warning", "info"]
    message: str


class ValidationResult(BaseModel):
    """Output of B8: track validation."""
    overall_valid: bool
    checks: list[ValidationCheck]
    critical_failures: int
    warnings: int
    retry_count: int
    final_status: Literal["validated", "validated_with_warnings", "failed"]


# ============================================================================
# Complete PersonalizedTrack (final output)
# ============================================================================

class PersonalizedTrack(BaseModel):
    """Complete personalized track (combination of all steps)."""
    validated_profile: ValidatedStudentProfile  # B1
    competency_set: CompetencySet  # B2
    ksa_matrix: KSAMatrix  # B3
    learning_units: LearningUnitsOutput  # B4
    hierarchy: HierarchyOutput  # B5
    lesson_blueprints: BlueprintsOutput  # B6
    schedule: ScheduleOutput  # B7
    validation: ValidationResult  # B8
