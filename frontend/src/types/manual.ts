/**
 * TypeScript types for manual debug mode
 */

export interface ManualSession {
  id: string
  profile_id: string
  profile_snapshot: Record<string, unknown>
  name: string
  description: string | null
  status: 'active' | 'archived'
  created_at: string
  updated_at: string
}

export interface ManualSessionListResponse {
  sessions: ManualSession[]
  total: number
}

export interface PromptVersion {
  id: string
  step_name: string
  version: number
  prompt_text: string
  change_description: string | null
  is_baseline: boolean
  created_at: string
}

export interface PromptStepSummary {
  step_name: string
  latest_version: number
  latest_prompt_id: string
  is_baseline: boolean
  created_at: string
}

export interface StepRunRequest {
  prompt_version_id?: string | null
  custom_prompt?: string | null
  input_data?: Record<string, unknown> | null
  llm_params?: Record<string, unknown> | null
  run_preprocessors?: boolean
  run_postprocessors?: boolean
  use_mock?: boolean
}

export interface StepRunResponse {
  id: string
  session_id: string
  step_name: string
  run_number: number
  prompt_version_id: string | null
  rendered_prompt: string | null
  input_data: Record<string, unknown> | null
  profile_variables: Record<string, unknown> | null
  llm_params: Record<string, unknown> | null
  raw_response: string | null
  parsed_result: Record<string, unknown> | null
  parse_error: string | null
  tokens_used: number | null
  duration_ms: number | null
  status: 'pending' | 'running' | 'completed' | 'failed'
  preprocessor_results: ProcessorRunResult[] | null
  postprocessor_results: ProcessorRunResult[] | null
  auto_evaluation: Record<string, unknown> | null
  llm_judge_evaluation: Record<string, unknown> | null
  user_rating: number | null
  user_notes: string | null
  created_at: string
}

export interface StepRunSummary {
  id: string
  run_number: number
  status: string
  duration_ms: number | null
  tokens_used: number | null
  user_rating: number | null
  created_at: string
}

export interface StepStatus {
  run_count: number
  status: string
  last_run_id: string | null
  last_rating: number | null
}

export interface StepStatusResponse {
  steps: Record<string, StepStatus>
}

export interface ProcessorRunResult {
  name: string
  passed: boolean
  output?: Record<string, unknown>
  message?: string
  error?: string
}

export interface ProcessorInfo {
  name: string
  type: 'pre' | 'post'
  applicable_steps: string[]
  description: string
}

export interface ProcessorConfigItem {
  processor_name: string
  processor_type: string
  execution_order: number
  enabled: boolean
  config_params: Record<string, unknown> | null
}

export const STEP_NAMES = [
  'B1_validate',
  'B2_competencies',
  'B3_ksa_matrix',
  'B4_learning_units',
  'B5_hierarchy',
  'B6_problem_formulations',
  'B7_schedule',
  'B8_validation',
] as const

export const STEP_SHORT_NAMES: Record<string, string> = {
  B1_validate: 'B1',
  B2_competencies: 'B2',
  B3_ksa_matrix: 'B3',
  B4_learning_units: 'B4',
  B5_hierarchy: 'B5',
  B6_problem_formulations: 'B6',
  B7_schedule: 'B7',
  B8_validation: 'B8',
}

export const STEP_DESCRIPTIONS: Record<string, string> = {
  B1_validate: 'Валидация и обогащение профиля',
  B2_competencies: 'Формулировка компетенций',
  B3_ksa_matrix: 'KSA-матрица',
  B4_learning_units: 'Учебные единицы',
  B5_hierarchy: 'Иерархия и уровни',
  B6_problem_formulations: 'Формулировки проблем (PBL)',
  B7_schedule: 'Сборка расписания',
  B8_validation: 'Валидация трека',
}
