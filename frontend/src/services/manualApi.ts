/**
 * API client for manual debug mode
 */

import type {
  ManualSession,
  ManualSessionListResponse,
  PromptVersion,
  PromptStepSummary,
  StepRunRequest,
  StepRunResponse,
  StepRunSummary,
  StepStatusResponse,
  ProcessorInfo,
  ProcessorConfigItem,
} from '@/types/manual'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new APIError(response.status, data.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

// Sessions
export async function createSession(profileId: string, name: string, description?: string): Promise<ManualSession> {
  return fetchAPI('/api/manual/sessions', {
    method: 'POST',
    body: JSON.stringify({ profile_id: profileId, name, description }),
  })
}

export async function listSessions(status?: string): Promise<ManualSessionListResponse> {
  const query = status ? `?status=${status}` : ''
  return fetchAPI(`/api/manual/sessions${query}`)
}

export async function getSession(id: string): Promise<ManualSession> {
  return fetchAPI(`/api/manual/sessions/${id}`)
}

export async function updateSession(id: string, data: {
  name?: string; description?: string; status?: string; profile_snapshot?: Record<string, unknown>
}): Promise<ManualSession> {
  return fetchAPI(`/api/manual/sessions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteSession(id: string): Promise<void> {
  await fetch(`${BASE_URL}/api/manual/sessions/${id}`, { method: 'DELETE' })
}

// Steps
export async function runStep(sessionId: string, stepName: string, request: StepRunRequest = {}): Promise<StepRunResponse> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/steps/${stepName}/run`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function getStepsStatus(sessionId: string): Promise<StepStatusResponse> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/steps`)
}

export async function getStepRuns(sessionId: string, stepName: string): Promise<StepRunSummary[]> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/steps/${stepName}/runs`)
}

export async function getRunDetail(sessionId: string, runId: string): Promise<StepRunResponse> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/runs/${runId}`)
}

export async function updateRunRating(sessionId: string, runId: string, rating: number | null, notes?: string): Promise<StepRunResponse> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/runs/${runId}/rating`, {
    method: 'PATCH',
    body: JSON.stringify({ user_rating: rating, user_notes: notes }),
  })
}

export async function requestLLMJudge(sessionId: string, runId: string, useMock: boolean = true): Promise<StepRunResponse> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/runs/${runId}/judge?use_mock=${useMock}`, {
    method: 'POST',
  })
}

// Prompts
export async function listPrompts(): Promise<{ steps: PromptStepSummary[] }> {
  return fetchAPI('/api/manual/prompts')
}

export async function getPromptVersions(stepName: string): Promise<PromptVersion[]> {
  return fetchAPI(`/api/manual/prompts/${stepName}/versions`)
}

export async function createPromptVersion(stepName: string, promptText: string, changeDescription?: string): Promise<PromptVersion> {
  return fetchAPI(`/api/manual/prompts/${stepName}`, {
    method: 'POST',
    body: JSON.stringify({ prompt_text: promptText, change_description: changeDescription }),
  })
}

export async function loadBaselines(): Promise<PromptVersion[]> {
  return fetchAPI('/api/manual/prompts/load-baseline', { method: 'POST' })
}

export async function rollbackPrompt(stepName: string, version: number): Promise<PromptVersion> {
  return fetchAPI(`/api/manual/prompts/${stepName}/rollback/${version}`, { method: 'POST' })
}

// Processors
export async function listProcessors(): Promise<ProcessorInfo[]> {
  return fetchAPI('/api/manual/processors')
}

export async function getProcessorConfig(sessionId: string, stepName: string): Promise<{
  step_name: string; processors: ProcessorConfigItem[]
}> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/processors/${stepName}`)
}

export async function setProcessorConfig(sessionId: string, stepName: string, processors: ProcessorConfigItem[]): Promise<{
  step_name: string; processors: ProcessorConfigItem[]
}> {
  return fetchAPI(`/api/manual/sessions/${sessionId}/processors/${stepName}`, {
    method: 'PUT',
    body: JSON.stringify({ processors }),
  })
}

export { APIError }
