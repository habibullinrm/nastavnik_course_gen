/**
 * TypeScript types matching backend API responses
 */

export interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface ProfileUploadResponse {
  id: string
  filename: string
  topic: string
  experience_level: string | null
  validation_result: ValidationResult
  created_at: string
}

export interface StudentProfile {
  id: string
  filename: string
  topic: string
  experience_level: string | null
  data: Record<string, unknown>
  validation_result: ValidationResult
  created_at: string
  updated_at: string
}

export interface ProfileSummary {
  id: string
  filename: string
  topic: string
  profile_name: string | null
  experience_level: string | null
  created_at: string
}

export interface GenerationMetadata {
  algorithm_version: string
  started_at: string
  finished_at: string
  steps_log: StepLog[]
  llm_calls_count: number
  total_tokens: number
  total_duration_sec: number
}

export interface StepLog {
  step_name: string
  duration_sec: number
  tokens_used: number
  success: boolean
  error_message: string | null
}

/** SSE step_update event data */
export interface SSEStepUpdate {
  step: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  description?: string
  duration_sec?: number
  tokens_used?: number
  summary?: Record<string, unknown>
  // batch fields
  track_id?: string
  batch_index?: number
}

/** SSE complete event data */
export interface SSECompleteEvent {
  total_duration_sec: number
  total_tokens: number
}

/** SSE cancelled event data */
export interface SSECancelledEvent {
  completed_steps: string[]
  last_step: string | null
}

/** SSE error event data */
export interface SSEErrorEvent {
  error: string
  failed_step?: string | null
}

/** Batch generation started response */
export interface BatchGenerationStartedResponse {
  batch_id: string
  track_ids: string[]
  status: string
  progress_url: string
}

/** SSE batch_complete event data */
export interface SSEBatchCompleteEvent {
  results: Array<{
    track_id: string
    batch_index: number
    status: string
    duration_sec: number | null
  }>
}

export interface PersonalizedTrack {
  id: string
  profile_id: string
  qa_report_id: string | null
  track_data: Record<string, unknown>
  generation_metadata: GenerationMetadata
  algorithm_version: string
  validation_b8: Record<string, unknown> | null
  status: string
  error_message: string | null
  generation_duration_sec: number | null
  batch_index: number | null
  created_at: string
  updated_at: string
}

export interface TrackSummary {
  id: string
  profile_id: string
  topic: string | null
  algorithm_version: string
  status: string
  generation_duration_sec: number | null
  created_at: string
}

export interface CDVPair {
  version_a_id: string
  version_b_id: string
  cdv_total: number
  cdv_topics: number
  cdv_subtopics: number
  cdv_activities: number
}

export interface TopicFrequency {
  topic_name: string
  count: number
  total_versions: number
  frequency_pct: number
}

export interface QAReport {
  id: string
  profile_id: string
  report_data: {
    cdv_matrix: CDVPair[]
    topic_frequency: TopicFrequency[]
    top_stable_topics: string[]
    top_unstable_topics: string[]
    mean_cdv: number
    cdv_std: number
    recommendation: string
    generated_at: string
  } | null
  batch_size: number
  completed_count: number
  mean_cdv: number | null
  cdv_std: number | null
  recommendation: string | null
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface QAReportSummary {
  id: string
  profile_id: string
  batch_size: number
  completed_count: number
  mean_cdv: number | null
  recommendation: string | null
  status: string
  created_at: string
}

export interface GenerationProgress {
  step: string
  progress: number
  message: string
}

/** Step descriptions for UI display */
export const STEP_DESCRIPTIONS: Record<string, string> = {
  B1: 'Валидация и обогащение профиля',
  B2: 'Формулировка компетенций',
  B3: 'KSA-матрица (Знания-Умения-Навыки)',
  B4: 'Проектирование учебных единиц',
  B5: 'Иерархия и уровни',
  B6: 'Формулировки проблем (PBL)',
  B7: 'Сборка расписания',
  B8: 'Валидация трека',
}

export interface FieldUsageItem {
  field_name: string
  used: boolean
  steps: string[]
}

export interface FieldUsageResponse {
  track_id: string
  used_fields: FieldUsageItem[]
  unused_fields: string[]
}

// ─── Profile Form Types (003-manual-profile) ──────────────────────────────

export interface ProfileFormTask {
  id: string
  description: string
  complexity_rank: number
}

export interface ProfileFormSubtask {
  id: string
  description: string
  parent_task_id: string
  required_skills: string[]
  required_knowledge: string[]
}

export interface ProfileFormBarrier {
  id: string
  description: string
  barrier_type: 'conceptual' | 'procedural' | 'motivational'
  related_task_id: string
}

export interface ProfileFormConcept {
  id: string
  term: string
  confusion_description: string
}

export interface ProfileFormScheduleDay {
  day_of_week: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday'
  available_minutes: number
}

export interface ProfileFormPracticeWindow {
  time_of_day: 'morning' | 'afternoon' | 'evening'
  duration_minutes: number
  device: 'phone' | 'laptop' | 'tablet'
}

export interface ProfileFormSuccessCriterion {
  id: string
  description: string
  metric: string
  measurable: boolean
}

export interface ProfileFormState {
  // Идентификатор профиля
  profile_name: string            // 🟡 IMPORTANT

  // Блок 0: Тема
  topic: string                   // 🔴 CRITICAL
  subject_area: string            // 🔴 CRITICAL
  topic_scope: string             // 🟡 IMPORTANT

  // Блок 1: Контекст и мотивация
  role: string                    // 🟡 IMPORTANT
  experience_level: 'zero' | 'beginner' | 'intermediate' | 'advanced' | ''  // 🔴
  formal_education: string        // 🟢 OPTIONAL
  identified_risks: string[]      // 🟡 IMPORTANT
  novice_mode: boolean            // derived: experience_level in ["zero","beginner"]
  motivation_external: string     // 🟡 IMPORTANT
  motivation_internal: string     // 🟢 OPTIONAL
  goal_type: 'applied' | 'fundamental' | 'mixed' | ''  // 🟡 IMPORTANT
  has_deadline: boolean           // 🟡 IMPORTANT
  deadline_date: string           // 🟡 IMPORTANT (ISO date, "" if no deadline)
  desired_outcomes: string[]      // 🔴 CRITICAL
  target_context: string          // 🟡 IMPORTANT
  outcome_source: 'user' | 'system_suggested' | 'mixed' | ''  // 🟢 OPTIONAL

  // Блок 2: Учебные задачи
  target_tasks: ProfileFormTask[]            // 🔴 CRITICAL
  tasks_source: 'user' | 'system_generated' | 'mixed' | ''  // 🟢
  task_hierarchy: ProfileFormTask[]          // 🔴 CRITICAL
  easiest_task_id: string         // 🔴 CRITICAL
  peak_task_id: string            // 🔴 CRITICAL
  subtasks: ProfileFormSubtask[]             // 🔴 CRITICAL
  subtasks_source: 'user' | 'system_generated' | 'mixed' | ''  // 🟢
  already_known_subtasks: string[]  // 🟡 IMPORTANT
  primary_context: string         // 🟡 IMPORTANT
  secondary_context: string       // 🟢 OPTIONAL
  context_type: 'academic' | 'professional' | 'personal' | 'general' | ''  // 🟡

  // Блок 3: Диагностика
  current_approach: string        // 🟡 IMPORTANT
  approach_gaps: string[]         // 🟡 IMPORTANT
  diagnostic_result: 'no_knowledge' | 'misconceptions' | 'partial' | 'solid_base' | ''  // 🔴
  key_barriers: ProfileFormBarrier[]         // 🟡 IMPORTANT
  barriers_source: 'user' | 'system_suggested' | 'auto_generated' | ''  // 🟢
  confusing_concepts: ProfileFormConcept[]   // 🔴 CRITICAL
  concepts_source: 'user' | 'auto_generated' | ''  // 🟢
  theory_format_preference: 'visual_schemas' | 'examples_first' | 'video' | 'discussion' | 'text_formulas' | 'mixed' | ''  // 🟡
  theory_format_details: string   // 🟢 OPTIONAL
  best_material_reference: string // 🟢 OPTIONAL

  // Блок 4: Практика
  instruction_format: string[]    // 🟡 IMPORTANT
  feedback_type: string[]         // 🟡 IMPORTANT
  practice_format: string[]       // 🟡 IMPORTANT
  daily_practice_minutes: number  // 🟡 IMPORTANT
  practice_windows: ProfileFormPracticeWindow[]  // 🟢 OPTIONAL
  needs_reminder: boolean         // 🟢 OPTIONAL
  mastery_signals: string[]       // 🟢 OPTIONAL
  support_tools: string[]         // 🟢 OPTIONAL

  // Блок 5: Организация
  weekly_hours: number            // 🔴 CRITICAL
  schedule: ProfileFormScheduleDay[]         // 🟡 IMPORTANT
  learning_format: 'self_paced' | 'mentored' | 'group' | 'mixed' | ''  // 🟡
  support_channel: string         // 🟢 OPTIONAL

  // Критерии успеха
  success_criteria: ProfileFormSuccessCriterion[]  // 🔴 CRITICAL
}

export interface ProfileFormResponse {
  id: string
  topic: string
  experience_level: string | null
  validation_result: ValidationResult
  created_at: string
  updated_at?: string
}

export const DEFAULT_PROFILE_FORM: ProfileFormState = {
  profile_name: '',
  topic: '', subject_area: '', topic_scope: '',
  role: '', experience_level: '', formal_education: '',
  identified_risks: [], novice_mode: false,
  motivation_external: '', motivation_internal: '',
  goal_type: '', has_deadline: false, deadline_date: '',
  desired_outcomes: [], target_context: '', outcome_source: 'user',
  target_tasks: [], tasks_source: 'user',
  task_hierarchy: [], easiest_task_id: '', peak_task_id: '',
  subtasks: [], subtasks_source: 'user', already_known_subtasks: [],
  primary_context: '', secondary_context: '', context_type: '',
  current_approach: '', approach_gaps: [], diagnostic_result: '',
  key_barriers: [], barriers_source: 'user',
  confusing_concepts: [], concepts_source: 'user',
  theory_format_preference: 'examples_first',
  theory_format_details: '', best_material_reference: '',
  instruction_format: ['checklist'],
  feedback_type: ['error_with_explanation'],
  practice_format: ['compare_with_standard'],
  daily_practice_minutes: 10, practice_windows: [],
  needs_reminder: true, mastery_signals: [], support_tools: ['progress_tracker'],
  weekly_hours: 5, schedule: [], learning_format: '', support_channel: '',
  success_criteria: [],
}
