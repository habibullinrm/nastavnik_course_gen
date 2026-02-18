'use client'

import { useState, useEffect, useCallback } from 'react'
import type { ProfileSummary, StudentProfile } from '@/types'
import { listProfiles, getProfile } from '@/services/api'

interface ProfilePickerModalProps {
  onSelect: (profileData: Record<string, unknown>) => void
  onClose: () => void
}

export default function ProfilePickerModal({ onSelect, onClose }: ProfilePickerModalProps) {
  const [profiles, setProfiles] = useState<ProfileSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selecting, setSelecting] = useState<string | null>(null)

  useEffect(() => {
    listProfiles()
      .then(setProfiles)
      .catch(() => setError('Не удалось загрузить список профилей'))
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = useCallback(async (id: string) => {
    setSelecting(id)
    try {
      const profile: StudentProfile = await getProfile(id)
      onSelect(profile.data as Record<string, unknown>)
      onClose()
    } catch {
      setError('Не удалось загрузить профиль')
    } finally {
      setSelecting(null)
    }
  }, [onSelect, onClose])

  // Close on backdrop click
  const handleBackdrop = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      onClick={handleBackdrop}
      data-testid="profile-picker-modal"
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Выбрать профиль из БД</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Закрыть"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-auto px-6 py-4">
          {loading && (
            <div className="text-center py-8 text-gray-500">Загрузка профилей...</div>
          )}
          {error && (
            <div className="bg-red-50 text-red-700 border border-red-200 rounded p-3 text-sm">{error}</div>
          )}
          {!loading && !error && profiles.length === 0 && (
            <div className="text-center py-8 text-gray-400">Нет сохранённых профилей</div>
          )}
          {!loading && profiles.length > 0 && (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Тема</th>
                  <th className="pb-2 font-medium">Уровень</th>
                  <th className="pb-2 font-medium">Дата</th>
                  <th className="pb-2" />
                </tr>
              </thead>
              <tbody className="divide-y">
                {profiles.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="py-3 pr-4 font-medium">{p.topic}</td>
                    <td className="py-3 pr-4 text-gray-500">{p.experience_level || '—'}</td>
                    <td className="py-3 pr-4 text-gray-400">
                      {new Date(p.created_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="py-3">
                      <button
                        onClick={() => handleSelect(p.id)}
                        disabled={selecting === p.id}
                        className="px-3 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                      >
                        {selecting === p.id ? 'Загрузка...' : 'Выбрать'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="px-6 py-3 border-t flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  )
}
