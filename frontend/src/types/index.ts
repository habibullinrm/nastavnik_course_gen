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
