/**
 * TypeScript-типы для разделов track_data (B1–B8 pipeline).
 * Основаны на Pydantic-схемах ml/src/schemas/pipeline_steps.py.
 */

// ─── B2: Competency Set ───────────────────────────────────────────────────────

export interface Competency {
  id: string
  title: string
  description: string
  related_task_ids: string[]
  related_outcome_indices: number[]
  level: 'foundational' | 'intermediate' | 'advanced' | 'integrative'
}

export interface CompetencySetData {
  competencies: Competency[]
  integral_competency_id: string
  competency_task_map: Record<string, string[]>
  competency_outcome_map: Record<string, number[]>
}

// ─── B3: KSA Matrix (Knowledge–Skills–Habits) ────────────────────────────────

export interface KnowledgeItem {
  id: string
  title: string
  description: string
  source: string
  required_for: string[]
}

export interface SkillItem {
  id: string
  title: string
  description: string
  source: string
  requires_knowledge: string[]
  required_for: string[]
}

export interface HabitItem {
  id: string
  title: string
  description: string
  source: string
  requires_skills: string[]
}

export interface KSADependencyEdge {
  from_id: string
  to_id: string
  dependency_type: 'prerequisite' | 'supports' | 'enables'
}

export interface KSAMatrixData {
  knowledge_items: KnowledgeItem[]
  skill_items: SkillItem[]
  habit_items: HabitItem[]
  dependency_graph: KSADependencyEdge[]
}

// ─── B4: Learning Units ───────────────────────────────────────────────────────

export interface TheoryUnit {
  id: string
  title: string
  knowledge_ids: string[]
  estimated_minutes: number
  content_outline: string
}

export interface PracticeUnit {
  id: string
  title: string
  skill_ids: string[]
  estimated_minutes: number
  exercises_outline: string
}

export interface AutomationUnit {
  id: string
  title: string
  habit_ids: string[]
  estimated_minutes: number
  practice_outline: string
}

export interface LearningUnitCluster {
  id: string
  title: string
  theory_units: string[]
  practice_units: string[]
  automation_units: string[]
  total_minutes: number
}

export interface LearningUnitsData {
  theory_units: TheoryUnit[]
  practice_units: PracticeUnit[]
  automation_units: AutomationUnit[]
  clusters: LearningUnitCluster[]
}

// ─── B5: Hierarchy ────────────────────────────────────────────────────────────

export interface TrackLevel {
  level: 'foundational' | 'intermediate' | 'advanced' | 'integrative'
  clusters: string[]
  estimated_weeks: number
}

export interface HierarchyData {
  levels: TrackLevel[]
  unit_sequence: string[]
  time_compression_applied: boolean
  total_weeks: number
}

// ─── B6: Lesson Blueprints (PBL) ─────────────────────────────────────────────

export interface ProblemFormulation {
  problem_statement: string
  expected_hypotheses: string[]
}

export interface LessonBlueprint {
  id: string
  cluster_id: string
  problem_formulation: ProblemFormulation
  knowledge_infusions: string[]
  practice_tasks: string[]
  contradictions: string[]
  synthesis_tasks: string[]
  reflection_questions: string[]
  fsm_rules: Record<string, unknown>
}

export interface LessonBlueprintsData {
  blueprints: LessonBlueprint[]
}

// ─── B7: Schedule ─────────────────────────────────────────────────────────────

export interface TrackDay {
  day_of_week: string
  learning_units: string[]
  total_minutes: number
}

export interface ScheduleCheckpoint {
  week_number: number
  title: string
  assessment_tasks: string[]
}

export interface TrackWeek {
  week_number: number
  level: string
  theme: string
  weekly_goals: string[]
  days: TrackDay[]
  checkpoint: ScheduleCheckpoint | null
}

export interface SupportPlan {
  scaffolding_techniques: string[]
  feedback_points: string[]
  resources: string[]
}

export interface ProgressMilestone {
  week: number
  title: string
  criteria: string[]
}

export interface ScheduleData {
  weeks: TrackWeek[]
  total_weeks: number
  checkpoints: ScheduleCheckpoint[]
  final_assessment: Record<string, unknown>
  support_plan: SupportPlan
  progress_milestones: ProgressMilestone[]
}

// ─── B8: Validation ───────────────────────────────────────────────────────────

export interface ValidationCheck {
  check_name: string
  passed: boolean
  severity: 'critical' | 'warning' | 'info'
  message: string
}

export interface ValidationData {
  overall_valid: boolean
  checks: ValidationCheck[]
  critical_failures: number
  warnings: number
  retry_count: number
  final_status: 'validated' | 'validated_with_warnings' | 'failed'
}

// ─── Сводный тип track_data ───────────────────────────────────────────────────

export interface TrackData {
  validated_profile?: Record<string, unknown>
  competency_set?: CompetencySetData
  ksa_matrix?: KSAMatrixData
  learning_units?: LearningUnitsData
  hierarchy?: HierarchyData
  lesson_blueprints?: LessonBlueprintsData
  schedule?: ScheduleData
  validation?: ValidationData
  [key: string]: unknown
}

// ─── Константы ────────────────────────────────────────────────────────────────

export const LEVEL_LABELS: Record<string, string> = {
  foundational: 'Базовый',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
  integrative: 'Интегративный',
}

export const DAY_LABELS: Record<string, string> = {
  monday: 'Пн',
  tuesday: 'Вт',
  wednesday: 'Ср',
  thursday: 'Чт',
  friday: 'Пт',
  saturday: 'Сб',
  sunday: 'Вс',
}
