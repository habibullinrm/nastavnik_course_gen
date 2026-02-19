/**
 * Страница детального просмотра трека.
 * Показывает все разделы track_data (B2–B8) через вкладки.
 */

'use client'

import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import TrackTabs, { TrackTabId } from '@/components/Track/TrackTabs'
import TrackMetadata from '@/components/TrackMetadata/TrackMetadata'
import CompetencyList from '@/components/Track/CompetencyList'
import KSAMatrix from '@/components/Track/KSAMatrix'
import TreeView from '@/components/TreeView/TreeView'
import LessonBlueprints from '@/components/Track/LessonBlueprints'
import WeeklySchedule from '@/components/WeeklySchedule/WeeklySchedule'
import FieldUsage from '@/components/FieldUsage/FieldUsage'
import { TrackData } from '@/types/track'
import { StepLog } from '@/types/index'

interface TrackDetail {
  id: string
  profile_id: string
  track_data: TrackData
  generation_metadata?: {
    steps_log?: StepLog[]
    llm_calls_count?: number
    total_tokens?: number
    total_duration_sec?: number
  }
  algorithm_version: string
  status: string
  error_message?: string | null
  generation_duration_sec?: number | null
  created_at: string
  updated_at: string
}

export default function TrackDetailPage() {
  const params = useParams()
  const trackId = params.id as string

  const [track, setTrack] = useState<TrackDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TrackTabId>('metadata')

  useEffect(() => {
    if (!trackId) return

    async function fetchTrack() {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
        const response = await fetch(`${apiUrl}/api/tracks/${trackId}`)

        if (!response.ok) {
          throw new Error(`Трек не найден (${response.status})`)
        }

        setTrack(await response.json())
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    }

    fetchTrack()
  }, [trackId])

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-600">Загрузка трека...</div>
      </div>
    )
  }

  if (error || !track) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'Трек не найден'}
        </div>
      </div>
    )
  }

  const td = track.track_data
  const topic = (td.validated_profile?.topic as string | undefined) ?? 'Персонализированный трек'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Шапка */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{topic}</h1>
              <div className="flex items-center gap-3 mt-1.5 text-sm text-gray-500">
                <span className="font-mono text-xs">{track.id}</span>
                <span>·</span>
                <span>v{track.algorithm_version}</span>
                <span>·</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                  track.status === 'completed' ? 'bg-green-100 text-green-800' :
                  track.status === 'failed' ? 'bg-red-100 text-red-800' :
                  track.status === 'cancelled' ? 'bg-gray-100 text-gray-600' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {track.status}
                </span>
              </div>
            </div>
            <Link
              href={`/profiles/${track.profile_id}`}
              className="shrink-0 text-sm text-blue-600 hover:underline"
            >
              ← Профиль
            </Link>
          </div>
        </div>
      </div>

      {/* Навигация по вкладкам */}
      <TrackTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Контент вкладок */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        {activeTab === 'metadata' && (
          <TrackMetadata track={track} />
        )}
        {activeTab === 'competencies' && (
          <CompetencyList data={td.competency_set} />
        )}
        {activeTab === 'ksa' && (
          <KSAMatrix data={td.ksa_matrix} />
        )}
        {activeTab === 'tree' && (
          <TreeView units={td.learning_units} hierarchy={td.hierarchy} />
        )}
        {activeTab === 'blueprints' && (
          <LessonBlueprints data={td.lesson_blueprints} />
        )}
        {activeTab === 'schedule' && (
          <WeeklySchedule data={td.schedule} />
        )}
        {activeTab === 'fields' && (
          <FieldUsage trackId={trackId} />
        )}
      </div>
    </div>
  )
}
