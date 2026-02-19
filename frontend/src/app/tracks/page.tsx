/**
 * Страница списка треков
 *
 * Отображает таблицу всех сгенерированных треков с фильтрацией по профилю.
 * При клике на трек открывается страница просмотра.
 */

'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

interface TrackSummary {
  id: string
  profile_id: string
  topic: string | null
  status: string
  generation_duration_sec: number | null
  created_at: string
  algorithm_version: string
}

export default function TracksListPage() {
  const [tracks, setTracks] = useState<TrackSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTracks()
  }, [])

  async function fetchTracks() {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
      const response = await fetch(`${apiUrl}/api/tracks/`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setTracks(data.tracks || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки треков')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-600">Загрузка треков...</div>
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
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Сгенерированные треки</h1>

      {tracks.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 mb-4">Пока нет сгенерированных треков</p>
          <Link
            href="/profiles"
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Выбрать профиль для генерации
          </Link>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тема
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Длительность
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Дата создания
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Версия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tracks.map((track) => (
                <tr key={track.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/tracks/${track.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {track.topic || `Трек ${track.id.slice(0, 8)}`}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full
                      ${track.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                      ${track.status === 'generating' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${track.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
                      ${track.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
                    `}>
                      {track.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {track.generation_duration_sec
                      ? `${Math.round(track.generation_duration_sec)}с`
                      : '—'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(track.created_at).toLocaleString('ru-RU')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {track.algorithm_version}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
