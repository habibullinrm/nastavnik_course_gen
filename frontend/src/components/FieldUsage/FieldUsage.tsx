/**
 * Компонент анализа использования полей профиля
 *
 * Отображает:
 * - Таблицу использованных полей (зеленый цвет)
 * - Таблицу неиспользованных полей (серый цвет)
 * - Указание шагов B1-B8, где поле было использовано
 * - Критичность полей (CRITICAL, IMPORTANT, OPTIONAL)
 */

'use client'

import React from 'react'

interface FieldUsageItem {
  field_name: string
  used: boolean
  steps: string[]
  criticality: string
}

interface FieldUsageData {
  track_id: string
  used_fields: FieldUsageItem[]
  unused_fields: FieldUsageItem[]
  total_fields: number
  used_count: number
  unused_count: number
  critical_unused_count: number
  important_unused_count: number
}

interface FieldUsageProps {
  trackId: string
}

export default function FieldUsage({ trackId }: FieldUsageProps) {
  const [data, setData] = React.useState<FieldUsageData | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const fetchFieldUsage = async () => {
      try {
        setLoading(true)
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/tracks/${trackId}/field-usage`)

        if (!response.ok) {
          throw new Error('Failed to fetch field usage data')
        }

        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchFieldUsage()
  }, [trackId])

  if (loading) {
    return (
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="text-gray-500">Загрузка анализа использования полей...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="text-red-600">Ошибка: {error}</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="text-gray-500">Нет данных</div>
      </div>
    )
  }

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
      case 'CRITICAL':
        return 'text-red-600 font-semibold'
      case 'IMPORTANT':
        return 'text-orange-600 font-medium'
      case 'OPTIONAL':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const getCriticalityBadge = (criticality: string) => {
    switch (criticality) {
      case 'CRITICAL':
        return '🔴'
      case 'IMPORTANT':
        return '🟡'
      case 'OPTIONAL':
        return '🟢'
      default:
        return ''
    }
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Использование полей профиля</h3>

      {/* Статистика */}
      <div className="mb-6 p-4 bg-gray-50 rounded border border-gray-200">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Всего полей</div>
            <div className="text-lg font-semibold">{data.total_fields}</div>
          </div>
          <div>
            <div className="text-gray-500">Использовано</div>
            <div className="text-lg font-semibold text-green-600">{data.used_count}</div>
          </div>
          <div>
            <div className="text-gray-500">Не использовано</div>
            <div className="text-lg font-semibold text-gray-600">{data.unused_count}</div>
          </div>
          <div>
            <div className="text-gray-500">Критичных неисп.</div>
            <div className="text-lg font-semibold text-red-600">{data.critical_unused_count}</div>
          </div>
        </div>
      </div>

      {/* Использованные поля */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-3 text-green-700">
          ✓ Использованные поля ({data.used_fields.length})
        </h4>
        {data.used_fields.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-green-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                    Поле
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                    Критичность
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                    Шаги использования
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.used_fields.map((field, idx) => (
                  <tr key={idx} className="hover:bg-green-50">
                    <td className="px-4 py-2 text-sm font-mono text-gray-900">
                      {field.field_name}
                    </td>
                    <td className={`px-4 py-2 text-sm ${getCriticalityColor(field.criticality)}`}>
                      {getCriticalityBadge(field.criticality)} {field.criticality}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {field.steps.length > 0 ? field.steps.join(', ') : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-gray-500 text-sm">Нет использованных полей</div>
        )}
      </div>

      {/* Неиспользованные поля */}
      <div>
        <h4 className="text-md font-medium mb-3 text-gray-700">
          ✗ Неиспользованные поля ({data.unused_fields.length})
        </h4>
        {data.unused_fields.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                    Поле
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase">
                    Критичность
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.unused_fields.map((field, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-mono text-gray-500">
                      {field.field_name}
                    </td>
                    <td className={`px-4 py-2 text-sm ${getCriticalityColor(field.criticality)}`}>
                      {getCriticalityBadge(field.criticality)} {field.criticality}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-green-600 text-sm">Все поля использованы!</div>
        )}
      </div>

      {/* Предупреждения */}
      {(data.critical_unused_count > 0 || data.important_unused_count > 0) && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h5 className="text-sm font-medium text-yellow-800 mb-1">⚠️ Предупреждение</h5>
          <ul className="text-sm text-yellow-700 list-disc ml-5">
            {data.critical_unused_count > 0 && (
              <li>Не использовано {data.critical_unused_count} критичных полей</li>
            )}
            {data.important_unused_count > 0 && (
              <li>Не использовано {data.important_unused_count} важных полей</li>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}
