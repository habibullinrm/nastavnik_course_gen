/**
 * Страница детального просмотра трека
 *
 * Функциональность:
 * - Загрузка трека по ID
 * - Табы: Дерево курса, Расписание, Метаданные, Поля профиля
 * - Отображение результатов валидации B8
 */

'use client'

import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import TreeView from '@/components/TreeView/TreeView'
import WeeklySchedule from '@/components/WeeklySchedule/WeeklySchedule'
import TrackMetadata from '@/components/TrackMetadata/TrackMetadata'
import FieldUsage from '@/components/FieldUsage/FieldUsage'

type TabType = 'tree' | 'schedule' | 'metadata' | 'fields'

interface Competency {
  id: string
  title?: string
  description?: string
}

interface KnowledgeItem {
  id: string
  title?: string
}

interface SkillItem {
  id: string
  title?: string
}

interface LearningUnit {
  id: string
  title: string
  type: string
  duration_minutes?: number
  is_checkpoint?: boolean
}

interface Day {
  day_index?: number
  learning_units?: LearningUnit[]
}

interface Week {
  week_index?: number
  days?: Day[]
}

interface TrackData {
  topic?: string
  competency_set?: {
    competencies?: Competency[]
  }
  ksa_matrix?: {
    knowledge_items?: KnowledgeItem[]
    skill_items?: SkillItem[]
  }
  learning_units?: LearningUnit[]
  schedule?: {
    weeks?: Week[]
  }
  [key: string]: unknown
}

interface TrackDetail {
  id: string
  profile_id: string
  qa_report_id?: string
  track_data: TrackData
  generation_metadata?: {
    [key: string]: unknown
  }
  algorithm_version: string
  validation_b8?: {
    valid: boolean
    errors?: string[]
  }
  status: string
  error_message?: string
  generation_duration_sec?: number
  batch_index?: number
  created_at: string
  updated_at: string
}

export default function TrackDetailPage() {
  const params = useParams()
  const trackId = params.id as string

  const [track, setTrack] = useState<TrackDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('tree')

  useEffect(() => {
    const fetchTrack = async () => {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/tracks/${trackId}`)

        if (!response.ok) {
          throw new Error(`Failed to fetch track: ${response.status}`)
        }

        const data = await response.json()
        setTrack(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    if (trackId) {
      fetchTrack()
    }
  }, [trackId])

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-xl font-semibold text-gray-700">Загрузка трека...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Ошибка</h2>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    )
  }

  if (!track) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-gray-500">Трек не найден</div>
      </div>
    )
  }

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'tree', label: 'Дерево курса', icon: '🌳' },
    { id: 'schedule', label: 'Расписание', icon: '📅' },
    { id: 'metadata', label: 'Метаданные', icon: '📊' },
    { id: 'fields', label: 'Поля профиля', icon: '🔍' },
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Заголовок */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {track.track_data?.topic || 'Персонализированный трек'}
        </h1>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>ID: {track.id}</span>
          <span>•</span>
          <span>Версия: {track.algorithm_version}</span>
          <span>•</span>
          <span
            className={`px-2 py-1 rounded-full text-xs font-semibold ${
              track.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : track.status === 'failed'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {track.status}
          </span>
        </div>
      </div>

      {/* Валидация B8 */}
      {track.validation_b8 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-md font-semibold text-blue-900 mb-2">
            ✓ Результат валидации B8
          </h3>
          <div className="text-sm text-blue-800">
            {track.validation_b8.valid ? (
              <span className="font-medium text-green-700">Трек прошел валидацию</span>
            ) : (
              <>
                <span className="font-medium text-red-700">Трек не прошел валидацию</span>
                {track.validation_b8.errors && (
                  <ul className="mt-2 list-disc ml-5">
                    {track.validation_b8.errors.map((err: string, idx: number) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Табы */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex gap-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Контент табов */}
      <div>
        {activeTab === 'tree' && <TreeView trackData={track.track_data} />}
        {activeTab === 'schedule' && <WeeklySchedule trackData={track.track_data} />}
        {activeTab === 'metadata' && <TrackMetadata track={track as unknown as Record<string, unknown>} />}
        {activeTab === 'fields' && <FieldUsage trackId={trackId} />}
      </div>
    </div>
  )
}
