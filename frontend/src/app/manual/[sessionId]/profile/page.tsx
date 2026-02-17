'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import type { ManualSession } from '@/types/manual'
import { getSession, updateSession } from '@/services/manualApi'

export default function ProfileEditorPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const router = useRouter()
  const [session, setSession] = useState<ManualSession | null>(null)
  const [jsonText, setJsonText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    (async () => {
      const sess = await getSession(sessionId)
      setSession(sess)
      setJsonText(JSON.stringify(sess.profile_snapshot, null, 2))
    })()
  }, [sessionId])

  const handleSave = async () => {
    setError(null)
    try {
      const parsed = JSON.parse(jsonText)
      setSaving(true)
      await updateSession(sessionId, { profile_snapshot: parsed })
      router.push(`/manual/${sessionId}`)
    } catch (e) {
      if (e instanceof SyntaxError) {
        setError(`Невалидный JSON: ${e.message}`)
      } else {
        setError(String(e))
      }
    } finally {
      setSaving(false)
    }
  }

  if (!session) return <div className="text-center py-8 text-gray-500">Загрузка...</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Редактор профиля — {session.name}</h1>
        <div className="flex gap-2">
          <button
            onClick={() => router.push(`/manual/${sessionId}`)}
            className="px-4 py-2 text-sm border rounded hover:bg-gray-50"
          >
            Назад
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      <textarea
        value={jsonText}
        onChange={(e) => setJsonText(e.target.value)}
        className="w-full h-[600px] px-4 py-3 border rounded-lg font-mono text-sm bg-white"
        spellCheck={false}
      />
    </div>
  )
}
