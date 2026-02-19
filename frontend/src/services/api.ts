/**
 * API client for backend communication
 */

import type {
  StudentProfile,
  ProfileSummary,
  ProfileUploadResponse,
  PersonalizedTrack,
  TrackSummary,
  QAReport,
  QAReportSummary,
  FieldUsageResponse,
  BatchGenerationStartedResponse,
  ProfileFormState,
  ProfileFormResponse,
} from '@/types'

// Empty string → relative URLs → Next.js rewrites proxy to backend container.
// Set NEXT_PUBLIC_API_URL only when running outside Docker (e.g. bare `npm run dev`).
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

class APIError extends Error {
  constructor(public status: number, message: string, public details?: unknown) {
    super(message)
    this.name = 'APIError'
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        response.status,
        errorData.detail || `HTTP ${response.status}`,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) {
      throw error
    }
    throw new APIError(0, `Network error: ${error}`)
  }
}

// Profile endpoints
export async function uploadProfile(file: File): Promise<ProfileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return fetchAPI<ProfileUploadResponse>('/api/profiles', {
    method: 'POST',
    body: formData,
  })
}

export async function getProfile(id: string): Promise<StudentProfile> {
  return fetchAPI<StudentProfile>(`/api/profiles/${id}`)
}

export async function listProfiles(): Promise<ProfileSummary[]> {
  const data = await fetchAPI<{ profiles: ProfileSummary[] }>('/api/profiles')
  return data.profiles
}

// Track endpoints
export async function generateTrack(profileId: string): Promise<{
  track_id: string
  status: string
  progress_url: string
}> {
  return fetchAPI('/api/tracks/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId }),
  })
}

export async function getTrack(id: string): Promise<PersonalizedTrack> {
  return fetchAPI<PersonalizedTrack>(`/api/tracks/${id}`)
}

export async function listTracks(profileId?: string): Promise<TrackSummary[]> {
  const query = profileId ? `?profile_id=${profileId}` : ''
  const data = await fetchAPI<{ tracks: TrackSummary[] }>(`/api/tracks${query}`)
  return data.tracks
}

export async function getFieldUsage(trackId: string): Promise<FieldUsageResponse> {
  return fetchAPI<FieldUsageResponse>(`/api/tracks/${trackId}/field-usage`)
}

export async function cancelTrack(trackId: string): Promise<{ status: string; track_id: string }> {
  return fetchAPI(`/api/tracks/${trackId}/cancel`, {
    method: 'POST',
  })
}

export async function generateTrackBatch(
  profileId: string,
  batchSize: number
): Promise<BatchGenerationStartedResponse> {
  return fetchAPI('/api/tracks/generate-batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId, batch_size: batchSize }),
  })
}

// QA endpoints
export async function generateBatch(
  profileId: string,
  batchSize: number
): Promise<{
  report_id: string
  profile_id: string
  batch_size: number
  status: string
  progress_url: string
}> {
  return fetchAPI('/api/qa/generate-batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_id: profileId, batch_size: batchSize }),
  })
}

export async function getQAReport(id: string): Promise<QAReport> {
  return fetchAPI<QAReport>(`/api/qa/reports/${id}`)
}

export async function listQAReports(profileId?: string): Promise<QAReportSummary[]> {
  const query = profileId ? `?profile_id=${profileId}` : ''
  const data = await fetchAPI<{ reports: QAReportSummary[] }>(
    `/api/qa/reports${query}`
  )
  return data.reports
}

// Export endpoints
export function getTrackExportURL(trackId: string): string {
  return `${BASE_URL}/api/export/tracks/${trackId}`
}

export function getQAReportExportURL(reportId: string): string {
  return `${BASE_URL}/api/export/qa-reports/${reportId}`
}

export function getQAReportAllExportURL(reportId: string): string {
  return `${BASE_URL}/api/export/qa-reports/${reportId}/all`
}

// SSE helpers
export function createProgressEventSource(url: string): EventSource {
  return new EventSource(`${BASE_URL}${url}`)
}

export { APIError }

// Profile Form endpoints (003-manual-profile)
export async function createProfileFromForm(profileData: ProfileFormState): Promise<ProfileFormResponse> {
  return fetchAPI<ProfileFormResponse>('/api/profiles/form', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profileData),
  })
}

export async function updateProfile(id: string, profileData: ProfileFormState): Promise<ProfileFormResponse> {
  return fetchAPI<ProfileFormResponse>(`/api/profiles/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profileData),
  })
}
