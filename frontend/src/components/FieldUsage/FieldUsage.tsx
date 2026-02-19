'use client'

import { useState, useEffect } from 'react'

interface FieldUsageItem {
  field_name: string
  used: boolean
  steps: string[]
  criticality: string
}

interface FieldUsageResponse {
  track_id: string
  used_fields: FieldUsageItem[]
  unused_fields: FieldUsageItem[]
  total_fields: number
  used_count: number
  unused_count: number
  critical_unused_count: number
  important_unused_count: number
}

const CRITICALITY_STYLES: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  IMPORTANT: 'bg-yellow-100 text-yellow-700',
  OPTIONAL: 'bg-gray-100 text-gray-500',
}

const CRITICALITY_LABELS: Record<string, string> = {
  CRITICAL: 'Критическое',
  IMPORTANT: 'Важное',
  OPTIONAL: 'Опциональное',
}

function FieldRow({ item }: { item: FieldUsageItem }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
      <span className={`shrink-0 w-2 h-2 rounded-full ${item.used ? 'bg-green-500' : 'bg-gray-300'}`} />
      <span className="text-sm font-mono text-gray-700 flex-1">{item.field_name}</span>
      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${CRITICALITY_STYLES[item.criticality] ?? 'bg-gray-100 text-gray-500'}`}>
        {CRITICALITY_LABELS[item.criticality] ?? item.criticality}
      </span>
      {item.steps.length > 0 && (
        <span className="text-xs text-gray-400 shrink-0">
          {item.steps.join(', ')}
        </span>
      )}
    </div>
  )
}

export default function FieldUsage({ trackId }: { trackId: string }) {
  const [data, setData] = useState<FieldUsageResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showUnused, setShowUnused] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const res = await fetch(`${apiUrl}/api/tracks/${trackId}/field-usage`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setData(await res.json())
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [trackId])

  if (loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-sm text-gray-500">Загрузка данных об использовании полей...</p>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
        {error || 'Данные не найдены'}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Сводка */}
      <div className="flex items-center gap-6 text-sm text-gray-600 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
        <span>
          <strong className="text-gray-900">{data.used_count}</strong> / {data.total_fields} полей использовано
        </span>
        {data.critical_unused_count > 0 && (
          <span className="text-red-600 font-medium">
            ⚠ {data.critical_unused_count} критических не использовано
          </span>
        )}
        {data.important_unused_count > 0 && (
          <span className="text-yellow-600 font-medium">
            {data.important_unused_count} важных не использовано
          </span>
        )}
      </div>

      {/* Использованные поля */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
          Использованные поля ({data.used_count})
        </h3>
        <div>
          {data.used_fields.map(item => (
            <FieldRow key={item.field_name} item={item} />
          ))}
        </div>
      </div>

      {/* Неиспользованные поля */}
      {data.unused_fields.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <button
            onClick={() => setShowUnused(o => !o)}
            className="w-full flex items-center justify-between text-sm font-semibold text-gray-700 uppercase tracking-wide"
          >
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-gray-300 inline-block" />
              Неиспользованные поля ({data.unused_count})
            </span>
            <span className="text-gray-400 text-xs font-normal normal-case">
              {showUnused ? '▲ скрыть' : '▼ показать'}
            </span>
          </button>
          {showUnused && (
            <div className="mt-3">
              {data.unused_fields.map(item => (
                <FieldRow key={item.field_name} item={item} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
