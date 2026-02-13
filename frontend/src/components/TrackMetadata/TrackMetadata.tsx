/**
 * Компонент метаданных генерации трека
 *
 * Отображает:
 * - Версию алгоритма
 * - Время генерации
 * - Количество LLM вызовов
 * - Токены
 */

'use client'

interface Track {
  id: string
  algorithm_version: string
  status: string
  generation_duration_sec?: number
  created_at: string
  error_message?: string
  generation_metadata?: {
    llm_calls_count?: number
    total_tokens?: number
    [key: string]: unknown
  }
}

interface TrackMetadataProps {
  track: Track
}

export default function TrackMetadata({ track }: TrackMetadataProps) {
  if (!track) {
    return null
  }

  const metadata = track.generation_metadata || {}

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Метаданные генерации</h3>

      <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-sm font-medium text-gray-500">Версия алгоритма</dt>
          <dd className="mt-1 text-sm text-gray-900">{track.algorithm_version || 'N/A'}</dd>
        </div>

        <div>
          <dt className="text-sm font-medium text-gray-500">Статус</dt>
          <dd className="mt-1">
            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full
              ${track.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
              ${track.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
              ${track.status === 'generating' ? 'bg-yellow-100 text-yellow-800' : ''}
            `}>
              {track.status}
            </span>
          </dd>
        </div>

        <div>
          <dt className="text-sm font-medium text-gray-500">Длительность генерации</dt>
          <dd className="mt-1 text-sm text-gray-900">
            {track.generation_duration_sec
              ? `${Math.round(track.generation_duration_sec)} сек`
              : 'N/A'
            }
          </dd>
        </div>

        <div>
          <dt className="text-sm font-medium text-gray-500">Дата создания</dt>
          <dd className="mt-1 text-sm text-gray-900">
            {new Date(track.created_at).toLocaleString('ru-RU')}
          </dd>
        </div>

        {metadata.llm_calls_count && (
          <div>
            <dt className="text-sm font-medium text-gray-500">LLM вызовов</dt>
            <dd className="mt-1 text-sm text-gray-900">{metadata.llm_calls_count}</dd>
          </div>
        )}

        {metadata.total_tokens && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Токенов</dt>
            <dd className="mt-1 text-sm text-gray-900">{metadata.total_tokens.toLocaleString()}</dd>
          </div>
        )}
      </dl>

      {track.error_message && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
          <h4 className="text-sm font-medium text-red-800 mb-1">Ошибка</h4>
          <p className="text-sm text-red-700">{track.error_message}</p>
        </div>
      )}
    </div>
  )
}
