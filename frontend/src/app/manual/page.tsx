'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import type { ManualSession } from '@/types/manual'
import type { ProfileSummary } from '@/types'
import { listSessions, createSession, deleteSession, loadBaselines } from '@/services/manualApi'
import { listProfiles } from '@/services/api'

export default function ManualSessionsPage() {
  const [sessions, setSessions] = useState<ManualSession[]>([])
  const [profiles, setProfiles] = useState<ProfileSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [selectedProfile, setSelectedProfile] = useState('')
  const [sessionName, setSessionName] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const load = async () => {
    setLoading(true)
    try {
      const [sessData, profData] = await Promise.all([
        listSessions(),
        listProfiles(),
      ])
      setSessions(sessData.sessions)
      setProfiles(profData)
      if (profData.length > 0 && !selectedProfile) {
        setSelectedProfile(profData[0].id)
      }
    } catch (e) {
      console.error('Failed to load:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!selectedProfile || !sessionName.trim()) return
    setCreating(true)
    try {
      await createSession(selectedProfile, sessionName)
      setSessionName('')
      setShowCreate(false)
      await load()
    } catch (e) {
      console.error('Failed to create session:', e)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Удалить сессию?')) return
    try {
      await deleteSession(id)
      await load()
    } catch (e) {
      console.error('Failed to delete:', e)
    }
  }

  const handleLoadBaselines = async () => {
    try {
      const result = await loadBaselines()
      alert(`Загружено ${result.length} baseline промптов`)
    } catch (e) {
      console.error('Failed to load baselines:', e)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ручной режим отладки</h1>
          <p className="text-gray-500 text-sm mt-1">
            Пошаговая отладка промптов и pipeline B1-B8
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleLoadBaselines}
            className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Загрузить baseline промпты
          </button>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Новая сессия
          </button>
        </div>
      </div>

      {showCreate && (
        <div className="p-4 border rounded-lg bg-white space-y-3">
          <h3 className="font-medium">Создать сессию</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Профиль</label>
              <select
                value={selectedProfile}
                onChange={(e) => setSelectedProfile(e.target.value)}
                className="w-full border rounded px-3 py-2 text-sm"
              >
                {profiles.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.topic} ({p.experience_level || 'N/A'})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Название</label>
              <input
                type="text"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="Отладка B2 компетенций"
                className="w-full border rounded px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCreate}
              disabled={creating || !sessionName.trim()}
              className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {creating ? 'Создание...' : 'Создать'}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 text-sm border rounded hover:bg-gray-50"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-gray-500">Загрузка...</div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">Нет сессий</p>
          <p className="text-sm mt-1">Создайте новую сессию для начала отладки</p>
        </div>
      ) : (
        <div className="space-y-2">
          {sessions.map(session => (
            <div key={session.id} className="p-4 border rounded-lg bg-white flex items-center justify-between hover:shadow-sm transition-shadow">
              <Link href={`/manual/${session.id}`} className="flex-1">
                <div className="flex items-center gap-3">
                  <span className={`inline-block w-2 h-2 rounded-full ${
                    session.status === 'active' ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <div>
                    <h3 className="font-medium">{session.name}</h3>
                    <p className="text-xs text-gray-400">
                      {new Date(session.created_at).toLocaleString('ru')}
                      {session.description && ` — ${session.description}`}
                    </p>
                  </div>
                </div>
              </Link>
              <button
                onClick={() => handleDelete(session.id)}
                className="text-sm text-red-400 hover:text-red-600 px-2"
              >
                Удалить
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
