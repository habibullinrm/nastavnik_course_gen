'use client'

import { useState, useEffect, useCallback } from 'react'
import type { PromptVersion } from '@/types/manual'
import { getPromptVersions, createPromptVersion, rollbackPrompt } from '@/services/manualApi'

interface PromptEditorProps {
  stepName: string
  selectedVersionId: string | null
  onVersionSelect: (versionId: string, promptText: string) => void
}

export default function PromptEditor({ stepName, selectedVersionId, onVersionSelect }: PromptEditorProps) {
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [editText, setEditText] = useState('')
  const [changeDesc, setChangeDesc] = useState('')
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)

  const loadVersions = useCallback(async (autoSelect: boolean = false) => {
    try {
      const data = await getPromptVersions(stepName)
      setVersions(data)
      // Auto-select latest version when switching steps or when explicitly requested
      if (data.length > 0 && autoSelect) {
        const latest = data[0]
        onVersionSelect(latest.id, latest.prompt_text)
        setEditText(latest.prompt_text)
      }
    } catch (e) {
      console.error('Failed to load versions:', e)
    }
    // onVersionSelect intentionally excluded — only called conditionally
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepName])

  // When step changes, always reload and auto-select the latest version
  useEffect(() => {
    setEditing(false)
    setChangeDesc('')
    loadVersions(true)
  }, [loadVersions])

  const handleSaveVersion = async () => {
    if (!editText.trim()) return
    setLoading(true)
    try {
      const newVersion = await createPromptVersion(stepName, editText, changeDesc || undefined)
      setEditing(false)
      setChangeDesc('')
      // Reload versions list first, then select the new version
      const data = await getPromptVersions(stepName)
      setVersions(data)
      onVersionSelect(newVersion.id, newVersion.prompt_text)
      setEditText(newVersion.prompt_text)
    } catch (e) {
      console.error('Failed to save version:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleRollback = async (version: number) => {
    setLoading(true)
    try {
      const newVersion = await rollbackPrompt(stepName, version)
      // Reload versions list first, then select
      const data = await getPromptVersions(stepName)
      setVersions(data)
      onVersionSelect(newVersion.id, newVersion.prompt_text)
      setEditText(newVersion.prompt_text)
    } catch (e) {
      console.error('Failed to rollback:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleVersionClick = (v: PromptVersion) => {
    onVersionSelect(v.id, v.prompt_text)
    setEditText(v.prompt_text)
  }

  const selectedVersion = versions.find(v => v.id === selectedVersionId)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">
          Промпт {selectedVersion ? `v${selectedVersion.version}` : ''}
          {selectedVersion?.is_baseline && <span className="ml-1 text-xs text-blue-600">(baseline)</span>}
        </h3>
        <div className="flex gap-2">
          <select
            value={selectedVersionId || ''}
            onChange={(e) => {
              const v = versions.find(v => v.id === e.target.value)
              if (v) handleVersionClick(v)
            }}
            className="text-sm border rounded px-2 py-1"
          >
            {versions.length === 0 && (
              <option value="">Нет версий</option>
            )}
            {versions.map(v => (
              <option key={v.id} value={v.id}>
                v{v.version} {v.is_baseline ? '(baseline)' : ''} {v.change_description ? `- ${v.change_description}` : ''}
              </option>
            ))}
          </select>
          <button
            onClick={() => setEditing(!editing)}
            className="px-2 py-1 text-sm border rounded hover:bg-gray-50"
          >
            {editing ? 'Отмена' : 'Редактировать'}
          </button>
        </div>
      </div>

      <textarea
        value={editText}
        onChange={(e) => setEditText(e.target.value)}
        readOnly={!editing}
        className={`w-full px-3 py-2 border rounded text-sm font-mono resize-y ${
          editing ? 'bg-white border-indigo-300' : 'bg-gray-50'
        }`}
        rows={10}
      />

      {editing && (
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={changeDesc}
            onChange={(e) => setChangeDesc(e.target.value)}
            placeholder="Что изменилось?"
            className="flex-1 px-3 py-1.5 border rounded text-sm"
          />
          <button
            onClick={handleSaveVersion}
            disabled={loading}
            className="px-4 py-1.5 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : 'Сохранить как новую версию'}
          </button>
        </div>
      )}

      {versions.length > 1 && !editing && (
        <details className="text-sm">
          <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
            История версий ({versions.length})
          </summary>
          <div className="mt-2 space-y-1">
            {versions.map(v => (
              <div key={v.id} className="flex items-center justify-between px-2 py-1 rounded hover:bg-gray-50">
                <div className="flex items-center gap-2">
                  <span className={v.id === selectedVersionId ? 'font-bold' : ''}>
                    v{v.version}
                  </span>
                  {v.is_baseline && <span className="text-xs text-blue-500">baseline</span>}
                  {v.change_description && <span className="text-gray-400">{v.change_description}</span>}
                </div>
                <button
                  onClick={() => handleRollback(v.version)}
                  className="text-xs text-indigo-600 hover:text-indigo-800"
                  disabled={loading}
                >
                  Откатить
                </button>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
