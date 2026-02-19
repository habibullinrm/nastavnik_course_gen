/**
 * Страница детального просмотра профиля студента.
 * Показывает информацию о профиле и ссылку на последний трек.
 */

'use client'

import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'

interface ProfileDetail {
  id: string
  filename: string
  topic: string
  experience_level: string | null
  data: Record<string, unknown>
  created_at: string
  updated_at: string
}

interface LastTrack {
  track_id: string
  status: string
  created_at: string
}

const EXPERIENCE_LABELS: Record<string, string> = {
  zero: 'Нулевой',
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
}

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-600',
  generating: 'bg-yellow-100 text-yellow-800',
  pending: 'bg-blue-100 text-blue-700',
  running: 'bg-blue-100 text-blue-700',
}

export default function ProfileDetailPage() {
  const params = useParams()
  const profileId = params.id as string

  const [profile, setProfile] = useState<ProfileDetail | null>(null)
  const [lastTrack, setLastTrack] = useState<LastTrack | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!profileId) return

    async function loadData() {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        const [profileRes, trackRes] = await Promise.allSettled([
          fetch(`${apiUrl}/api/profiles/${profileId}`),
          fetch(`${apiUrl}/api/profiles/${profileId}/last-track`),
        ])

        if (profileRes.status === 'fulfilled' && profileRes.value.ok) {
          setProfile(await profileRes.value.json())
        } else {
          setError('Профиль не найден')
          return
        }

        if (trackRes.status === 'fulfilled' && trackRes.value.ok) {
          setLastTrack(await trackRes.value.json())
        }
        // 404 = нет треков — это нормально
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [profileId])

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-600">Загрузка профиля...</div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'Профиль не найден'}
        </div>
        <Link href="/profiles" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
          ← К списку профилей
        </Link>
      </div>
    )
  }

  const profileName = profile.data?.profile_name as string | undefined

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Навигация */}
      <div className="mb-6">
        <Link href="/profiles" className="text-sm text-blue-600 hover:underline">
          ← К списку профилей
        </Link>
      </div>

      {/* Заголовок */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {profileName || profile.topic}
        </h1>
        {profileName && (
          <p className="text-gray-500 mt-1">{profile.topic}</p>
        )}
      </div>

      {/* Блок: последний трек */}
      <div className={`rounded-lg border p-5 mb-6 ${
        lastTrack
          ? 'border-green-200 bg-green-50'
          : 'border-gray-200 bg-gray-50'
      }`}>
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
          Учебный трек
        </h2>

        {lastTrack ? (
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  STATUS_STYLES[lastTrack.status] ?? 'bg-gray-100 text-gray-600'
                }`}>
                  {lastTrack.status}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(lastTrack.created_at).toLocaleString('ru-RU')}
                </span>
              </div>
              <p className="text-xs text-gray-400 font-mono">{lastTrack.track_id}</p>
            </div>
            <Link
              href={`/tracks/${lastTrack.track_id}`}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shrink-0"
            >
              Открыть последний трек →
            </Link>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-gray-500">Треки для этого профиля не найдены.</p>
            <Link
              href={`/tracks/generate?profile_id=${profile.id}`}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 shrink-0"
            >
              Генерировать трек →
            </Link>
          </div>
        )}
      </div>

      {/* Основные данные профиля */}
      <div className="bg-white border border-gray-200 rounded-lg p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
          Данные профиля
        </h2>
        <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
          <div>
            <dt className="text-gray-500">Тема</dt>
            <dd className="font-medium text-gray-900 mt-0.5">{profile.topic}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Уровень</dt>
            <dd className="font-medium text-gray-900 mt-0.5">
              {EXPERIENCE_LABELS[profile.experience_level ?? ''] ?? profile.experience_level ?? '—'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Создан</dt>
            <dd className="font-medium text-gray-900 mt-0.5">
              {new Date(profile.created_at).toLocaleString('ru-RU')}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Обновлён</dt>
            <dd className="font-medium text-gray-900 mt-0.5">
              {new Date(profile.updated_at).toLocaleString('ru-RU')}
            </dd>
          </div>
        </dl>
      </div>

      {/* Действия */}
      <div className="flex gap-3">
        <Link
          href={`/profiles/${profile.id}/edit`}
          className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
        >
          Редактировать профиль
        </Link>
        <Link
          href={`/tracks/generate?profile_id=${profile.id}`}
          className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700"
        >
          Генерировать новый трек
        </Link>
      </div>
    </div>
  )
}
