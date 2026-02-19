'use client'

import { useState } from 'react'
import { ScheduleData, LEVEL_LABELS, DAY_LABELS } from '@/types/track'

interface WeeklyScheduleProps {
  data?: ScheduleData
}

/** Расписание занятий из шага B7. Checkpoint-недели визуально выделены. */
export default function WeeklySchedule({ data }: WeeklyScheduleProps) {
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set())

  if (!data || !data.weeks?.length) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-sm text-gray-500">Расписание не сгенерировано</p>
        <p className="text-xs text-gray-400 mt-1">Шаг B7</p>
      </div>
    )
  }

  function toggleWeek(weekNumber: number) {
    setExpandedWeeks(prev => {
      const next = new Set(prev)
      if (next.has(weekNumber)) {
        next.delete(weekNumber)
      } else {
        next.add(weekNumber)
      }
      return next
    })
  }

  const totalMinutes = data.weeks.reduce(
    (sum, w) => sum + w.days.reduce((s, d) => s + d.total_minutes, 0),
    0
  )

  return (
    <div className="space-y-4">
      {/* Итоги */}
      <div className="flex items-center gap-6 text-sm text-gray-600 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
        <span>
          <strong className="text-gray-900">{data.total_weeks}</strong> нед.
        </span>
        <span>
          <strong className="text-gray-900">{Math.round(totalMinutes / 60)}</strong> часов всего
        </span>
        <span>
          <strong className="text-gray-900">{data.checkpoints?.length ?? 0}</strong> контрольных точек
        </span>
        {data.final_assessment?.type && (
          <span>
            Итоговая: <strong className="text-gray-900">{String(data.final_assessment.type)}</strong>
          </span>
        )}
      </div>

      {/* Список недель */}
      <div className="space-y-2">
        {data.weeks.map(week => {
          const hasCheckpoint = week.checkpoint != null
          const isExpanded = expandedWeeks.has(week.week_number)
          const weekMinutes = week.days.reduce((s, d) => s + d.total_minutes, 0)

          return (
            <div
              key={week.week_number}
              className={`border rounded-lg overflow-hidden ${
                hasCheckpoint
                  ? 'border-amber-300 bg-amber-50'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <button
                onClick={() => toggleWeek(week.week_number)}
                className="w-full flex items-center gap-4 p-4 text-left hover:bg-black/5 transition-colors"
              >
                {/* Номер недели */}
                <span
                  className={`shrink-0 w-8 h-8 rounded-full text-xs font-bold flex items-center justify-center ${
                    hasCheckpoint
                      ? 'bg-amber-400 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {week.week_number}
                </span>

                {/* Тема */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{week.theme}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {LEVEL_LABELS[week.level] ?? week.level} · {weekMinutes} мин
                  </p>
                </div>

                {/* Бейджи */}
                <div className="flex items-center gap-2 shrink-0">
                  {hasCheckpoint && (
                    <span className="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full font-medium">
                      ✓ Контрольная точка
                    </span>
                  )}
                  <span className="text-gray-400 text-xs">{isExpanded ? '▲' : '▼'}</span>
                </div>
              </button>

              {isExpanded && (
                <div className="border-t border-gray-100 px-4 pb-4 pt-3">
                  {/* Цели недели */}
                  {week.weekly_goals?.length > 0 && (
                    <div className="mb-3">
                      <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                        Цели недели
                      </h5>
                      <ul className="space-y-1">
                        {week.weekly_goals.map((g, i) => (
                          <li key={i} className="text-sm text-gray-700 flex gap-2">
                            <span className="text-gray-400 shrink-0">→</span>
                            <span>{g}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Расписание по дням */}
                  {week.days?.length > 0 && (
                    <div className="mb-3">
                      <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                        Дни
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {week.days.map((day, i) => (
                          <div
                            key={i}
                            className="text-xs bg-gray-100 rounded px-2 py-1 text-gray-600"
                          >
                            <span className="font-medium">
                              {DAY_LABELS[day.day_of_week] ?? day.day_of_week}
                            </span>
                            <span className="text-gray-400 ml-1">
                              {day.total_minutes} мин
                              {day.learning_units?.length > 0 && ` · ${day.learning_units.length} юн.`}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Контрольная точка */}
                  {hasCheckpoint && week.checkpoint && (
                    <div className="bg-amber-100 border border-amber-200 rounded p-3">
                      <h5 className="text-xs font-semibold text-amber-800 mb-1.5">
                        Контрольная точка: {week.checkpoint.title}
                      </h5>
                      {week.checkpoint.assessment_tasks?.length > 0 && (
                        <ul className="space-y-1">
                          {week.checkpoint.assessment_tasks.map((t, i) => (
                            <li key={i} className="text-xs text-amber-700 flex gap-1.5">
                              <span>•</span>
                              <span>{t}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Итоговая аттестация */}
      {data.final_assessment && (
        <div className="border border-gray-200 bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Итоговая аттестация</h4>
          <dl className="text-sm text-gray-600 space-y-1">
            {data.final_assessment.type && (
              <div className="flex gap-2">
                <dt className="text-gray-400">Тип:</dt>
                <dd>{String(data.final_assessment.type)}</dd>
              </div>
            )}
            {data.final_assessment.description && (
              <div className="flex gap-2">
                <dt className="text-gray-400">Описание:</dt>
                <dd>{String(data.final_assessment.description)}</dd>
              </div>
            )}
          </dl>
        </div>
      )}
    </div>
  )
}
