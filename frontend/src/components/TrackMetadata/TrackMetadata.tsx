'use client'

import { StepLog } from '@/types/index'

const STEPS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']

const STEP_DESCRIPTIONS: Record<string, string> = {
  B1: 'Валидация и обогащение профиля',
  B2: 'Формулировка компетенций',
  B3: 'KSA-матрица (Знания-Умения-Навыки)',
  B4: 'Проектирование учебных единиц',
  B5: 'Иерархия и уровни',
  B6: 'Формулировки проблем (PBL)',
  B7: 'Сборка расписания',
  B8: 'Валидация трека',
}

interface TrackMetadataProps {
  track: {
    id: string
    algorithm_version: string
    status: string
    generation_duration_sec?: number | null
    created_at: string
    generation_metadata?: {
      steps_log?: StepLog[]
      started_at?: string
      finished_at?: string
      llm_calls_count?: number
      total_tokens?: number
      total_duration_sec?: number
    }
  }
}

// Реальные имена шагов: 'B1_validate', 'B2_competencies', etc. — ищем по префиксу 'B1', 'B2', ...
function getStepStatus(stepPrefix: string, stepsLog: StepLog[] | undefined, trackStatus: string) {
  if (!stepsLog) {
    return trackStatus === 'generating' ? 'pending' : 'unknown'
  }
  const log = stepsLog.find(s => s.step_name === stepPrefix || s.step_name.startsWith(stepPrefix + '_'))
  if (!log) {
    return trackStatus === 'generating' ? 'pending' : 'not_run'
  }
  return log.success ? 'completed' : 'failed'
}

function StepStatusBadge({ status, durationSec }: { status: string; durationSec?: number }) {
  const configs: Record<string, { label: string; cls: string }> = {
    completed: { label: 'Завершён', cls: 'bg-green-100 text-green-800' },
    failed: { label: 'Ошибка', cls: 'bg-red-100 text-red-800' },
    pending: { label: 'В процессе...', cls: 'bg-yellow-100 text-yellow-800' },
    not_run: { label: 'Не выполнен', cls: 'bg-gray-100 text-gray-500' },
    unknown: { label: '—', cls: 'bg-gray-100 text-gray-400' },
  }
  const cfg = configs[status] ?? configs.unknown
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.cls}`}>
      {cfg.label}
      {durationSec !== undefined && status === 'completed' && (
        <span className="opacity-70">{durationSec.toFixed(1)}s</span>
      )}
    </span>
  )
}

/** Метаданные трека: статусы шагов B1–B8, время генерации, версия алгоритма. */
export default function TrackMetadata({ track }: TrackMetadataProps) {
  const stepsLog = track.generation_metadata?.steps_log
  const stepsMap = new Map<string, StepLog>()
  stepsLog?.forEach(s => stepsMap.set(s.step_name, s))

  return (
    <div className="space-y-6">
      {/* Общая информация */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
          Общая информация
        </h3>
        <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
          <div>
            <dt className="text-gray-500">Версия алгоритма</dt>
            <dd className="font-medium text-gray-900 mt-0.5">{track.algorithm_version}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Статус</dt>
            <dd className="mt-0.5">
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                track.status === 'completed' ? 'bg-green-100 text-green-800' :
                track.status === 'failed' ? 'bg-red-100 text-red-800' :
                track.status === 'cancelled' ? 'bg-gray-100 text-gray-600' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {track.status}
              </span>
            </dd>
          </div>
          {track.generation_duration_sec !== undefined && track.generation_duration_sec !== null && (
            <div>
              <dt className="text-gray-500">Время генерации</dt>
              <dd className="font-medium text-gray-900 mt-0.5">
                {track.generation_duration_sec.toFixed(1)} сек
              </dd>
            </div>
          )}
          {track.generation_metadata?.total_tokens !== undefined && (
            <div>
              <dt className="text-gray-500">Токенов использовано</dt>
              <dd className="font-medium text-gray-900 mt-0.5">
                {track.generation_metadata.total_tokens.toLocaleString('ru-RU')}
              </dd>
            </div>
          )}
          {track.generation_metadata?.llm_calls_count !== undefined && (
            <div>
              <dt className="text-gray-500">LLM-вызовов</dt>
              <dd className="font-medium text-gray-900 mt-0.5">
                {track.generation_metadata.llm_calls_count}
              </dd>
            </div>
          )}
          <div>
            <dt className="text-gray-500">Создан</dt>
            <dd className="font-medium text-gray-900 mt-0.5">
              {new Date(track.created_at).toLocaleString('ru-RU')}
            </dd>
          </div>
        </dl>
      </div>

      {/* Статусы шагов */}
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
          Шаги генерации
        </h3>
        <div className="space-y-2">
          {STEPS.map(step => {
            const log = stepsLog?.find(s => s.step_name === step || s.step_name.startsWith(step + '_'))
            const status = getStepStatus(step, stepsLog, track.status)
            return (
              <div key={step} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-gray-400 w-6">{step}</span>
                  <span className="text-sm text-gray-700">{STEP_DESCRIPTIONS[step]}</span>
                </div>
                <StepStatusBadge
                  status={status}
                  durationSec={log?.duration_sec}
                />
              </div>
            )
          })}
        </div>
      </div>

      {/* Ошибки шагов */}
      {stepsLog?.some(s => !s.success && s.error_message) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-5">
          <h3 className="text-sm font-semibold text-red-700 mb-3">Ошибки</h3>
          <ul className="space-y-2">
            {stepsLog.filter(s => !s.success && s.error_message).map((s, i) => (
              <li key={i} className="text-sm text-red-600">
                <span className="font-mono font-bold">{s.step_name}:</span>{' '}
                {s.error_message}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
