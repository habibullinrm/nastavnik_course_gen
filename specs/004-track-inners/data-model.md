# Data Model: Просмотр внутреннего содержимого трека

**Feature**: 004-track-inners
**Date**: 2026-02-18
**Phase**: 1 — Design

## Существующие сущности (без изменений)

### PersonalizedTrack (БД)

```
id: UUID
profile_id: UUID → StudentProfile
track_data: JSONB          — все выходы B1–B8
generation_metadata: JSONB
algorithm_version: str
validation_b8: JSONB | null
status: str                — 'generating' | 'completed' | 'failed' | 'cancelled'
error_message: str | null
generation_duration_sec: float | null
batch_index: int | null
created_at: datetime
updated_at: datetime
```

### StudentProfile (БД)

```
id: UUID
filename: str
topic: str
data: JSONB                — включает profile_name, topic, experience_level и все поля профиля
validation_result: JSONB
created_at: datetime
updated_at: datetime
```

## TypeScript-типы (новые / расширения)

### track_data — вложенные структуры

```typescript
// B2
interface CompetencySetData {
  competencies: Competency[]
  integral_competency_id: string
  competency_task_map: Record<string, string[]>
  task_competency_map: Record<string, string[]>
}

interface Competency {
  id: string
  title: string
  description: string
  related_task_ids: string[]
  level: string
}

// B3
interface KSAMatrixData {
  knowledge_items: KSAItem[]
  skill_items: KSAItem[]
  habit_items: KSAItem[]
  dependency_graph: KSADependency[]
}

interface KSAItem {
  id: string
  title: string
  description: string
  related_competency_ids: string[]
  complexity_level?: number
  is_prerequisite?: boolean
  practice_count_required?: number
  automation_level?: string
}

interface KSADependency {
  from_id: string
  to_id: string
  dependency_type: 'prerequisite' | 'supports' | 'enables'
}

// B4
interface LearningUnitsData {
  theory_units: LearningUnit[]
  practice_units: LearningUnit[]
  automation_units: LearningUnit[]
  clusters: Cluster[]
}

interface LearningUnit {
  id: string
  title: string
  description: string
  ksa_item_ids: string[]
  duration_minutes: number
  format?: string
  practice_type?: string
  repetition_count?: number
}

interface Cluster {
  id: string
  title: string
  theory_units: string[]
  practice_units: string[]
  automation_units: string[]
  total_minutes: number
}

// B5
interface HierarchyData {
  levels: HierarchyLevel[]
  unit_sequence: UnitSequenceItem[]
  time_compression_applied: boolean
  total_weeks: number
}

interface HierarchyLevel {
  level: 'foundational' | 'intermediate' | 'advanced' | 'integrative'
  clusters: string[]
  estimated_weeks: number
}

interface UnitSequenceItem {
  unit_id: string
  unit_type: 'theory' | 'practice' | 'automation'
  position: number
  week_number: number
}

// B6
interface LessonBlueprintsData {
  blueprints: LessonBlueprint[]
}

interface LessonBlueprint {
  id: string
  cluster_id: string
  problem_formulation: {
    problem_statement: string
    expected_hypotheses: string[]
  }
  knowledge_infusions: string[]
  practice_tasks: string[]
  contradictions: string[]
  synthesis_tasks: string[]
  reflection_questions: string[]
  fsm_rules: unknown[]
}

// B7
interface ScheduleData {
  weeks: ScheduleWeek[]
  checkpoints: ScheduleCheckpoint[]
  final_assessment: FinalAssessment
  support_plan: SupportPlan
  progress_milestones: ProgressMilestone[]
}

interface ScheduleWeek {
  week_number: number
  level: number
  theme: string
  weekly_goals: string[]
  days: ScheduleDay[]
  checkpoint: WeekCheckpoint | null
}

interface ScheduleDay {
  day_of_week: string
  units: ScheduleUnit[]
}

interface ScheduleUnit {
  unit_id: string
  unit_type: string
  duration_minutes: number
}

interface WeekCheckpoint {
  has_checkpoint: boolean
  description: string
}

interface ScheduleCheckpoint {
  week_number: number
  type: string
  description: string
  success_criteria: string[]
}

interface FinalAssessment {
  type: string
  description: string
  criteria: string[]
}

interface SupportPlan {
  reminders: string[]
  milestones: string[]
}

interface ProgressMilestone {
  week_number: number
  milestone_description: string
}

// B8
interface ValidationData {
  overall_valid: boolean
  checks: ValidationCheck[]
  critical_failures: number   // count
  warnings: number            // count
  retry_count: number
  final_status: 'validated' | 'validated_with_warnings' | 'failed'
}

interface ValidationCheck {
  check_name: string
  passed: boolean
  severity: 'critical' | 'warning' | 'info'
  message: string
}
```

### PersonalizedTrack (расширенный TypeScript-тип)

```typescript
interface PersonalizedTrack {
  // ... existing fields ...
  track_data: {
    validated_profile?: Record<string, unknown>
    competency_set?: CompetencySetData
    ksa_matrix?: KSAMatrixData
    learning_units?: LearningUnitsData
    hierarchy?: HierarchyData
    lesson_blueprints?: LessonBlueprintsData
    schedule?: ScheduleData
    validation?: ValidationData
  }
}
```

## Состояния и переходы

### Статусы трека (status)

```
generating → completed
generating → failed
generating → cancelled
```

### Логика отображения вкладок

| Статус трека | Завершённый шаг | Незавершённый шаг |
|--------------|-----------------|-------------------|
| completed    | Данные          | «Не выполнялся»   |
| failed       | Данные          | «Ошибка генерации»|
| cancelled    | Данные          | «Отменено»        |
| generating   | Данные          | «В процессе...»   |

### Связи между сущностями

```
StudentProfile → PersonalizedTrack (1:M по profile_id)
Competency → KSAItem (M:M через related_competency_ids)
Competency → LearningUnit (через ksa_item_ids → KSAItem → related_competency_ids)
Cluster → LearningUnit (через unit_ids)
HierarchyLevel → Cluster (через cluster_ids)
LessonBlueprint → Cluster (через cluster_id)
UnitSequenceItem → ScheduleWeek (через week_number)
```

## Новые API-запросы

Нет новых endpoint'ов для track_data — данные уже возвращаются в `GET /api/tracks/{track_id}`.

**Единственное изменение**: добавить `GET /api/profiles/{profile_id}/last-track` → редирект или данные последнего трека (для US4).
