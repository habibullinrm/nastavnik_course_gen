/**
 * Страница списка профилей
 *
 * Отображает все загруженные профили студентов.
 * При клике открывается детальная страница профиля.
 */

'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

interface ProfileSummary {
  id: string
  topic: string
  profile_name: string | null
  filename: string
  experience_level: string | null
  created_at: string
}

export default function ProfilesListPage() {
  const [profiles, setProfiles] = useState<ProfileSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchProfiles()
  }, [])

  async function fetchProfiles() {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/profiles/`)
      if (response.status === 404) {
        // API не реализовано пока
        setProfiles([])
        return
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setProfiles(data.profiles || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки профилей')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-600">Загрузка профилей...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <h2 className="font-semibold mb-2">Ошибка</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Профили студентов</h1>
        <Link
          href="/profiles/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          + Создать профиль
        </Link>
      </div>

      {profiles.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 mb-4">Пока нет сохранённых профилей</p>
          <Link
            href="/profiles/new"
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            + Создать профиль
          </Link>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/3">
                  Тема
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Уровень
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                  Дата создания
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {profiles.map((profile) => (
                <tr key={profile.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <span className="text-gray-900 font-medium">
                      {profile.profile_name || profile.topic}
                    </span>
                    {profile.profile_name && (
                      <div className="text-xs text-gray-400 mt-0.5">{profile.topic}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {profile.experience_level || '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(profile.created_at).toLocaleString('ru-RU')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <Link
                      href={`/profiles/${profile.id}/edit`}
                      className="text-blue-600 hover:text-blue-800 font-medium mr-3"
                    >
                      Редактировать
                    </Link>
                    <Link
                      href={`/tracks/generate?profile_id=${profile.id}`}
                      className="text-green-600 hover:text-green-800 font-medium"
                    >
                      Генерировать →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6">
        <Link
          href="/"
          className="inline-block px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          ← На главную
        </Link>
      </div>
    </div>
  )
}
