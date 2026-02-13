/**
 * Компонент понедельного расписания курса
 *
 * Отображает:
 * - Недели курса
 * - Дни недели с учебными единицами
 * - Длительности каждой единицы
 * - Checkpoints (выделены особым образом)
 */

'use client'

import { useState } from 'react'

interface LearningUnit {
  id?: string
  title: string
  type: string
  duration_minutes?: number
  is_checkpoint?: boolean
}

interface Day {
  day_index?: number
  learning_units?: LearningUnit[]
}

interface Week {
  week_index?: number
  days?: Day[]
}

interface Schedule {
  weeks?: Week[]
}

interface TrackData {
  schedule?: Schedule
}

interface WeeklyScheduleProps {
  trackData: TrackData | null
}

export default function WeeklySchedule({ trackData }: WeeklyScheduleProps) {
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([0]))

  if (!trackData) {
    return <div className="text-gray-500">Нет данных для отображения</div>
  }

  // Извлечь расписание из track_data
  const schedule = trackData.schedule
  const weeks: Week[] = schedule?.weeks || []

  const toggleWeek = (weekIndex: number) => {
    const newExpanded = new Set(expandedWeeks)
    if (newExpanded.has(weekIndex)) {
      newExpanded.delete(weekIndex)
    } else {
      newExpanded.add(weekIndex)
    }
    setExpandedWeeks(newExpanded)
  }

  const formatDuration = (minutes: number | undefined) => {
    if (!minutes) return 'N/A'
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0 && mins > 0) {
      return `${hours}ч ${mins}м`
    } else if (hours > 0) {
      return `${hours}ч`
    } else {
      return `${mins}м`
    }
  }

  const getDayName = (dayIndex: number) => {
    const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return days[dayIndex] || `День ${dayIndex + 1}`
  }

  if (weeks.length === 0) {
    return (
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Расписание</h3>
        <div className="text-gray-500">Расписание не сгенерировано</div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Понедельное расписание</h3>

      <div className="space-y-4">
        {weeks.map((week, weekIdx) => {
          const weekIndex = week.week_index ?? weekIdx
          const isExpanded = expandedWeeks.has(weekIndex)
          const days = week.days || []

          // Подсчитать общее время недели
          let totalWeekMinutes = 0
          days.forEach(day => {
            day.learning_units?.forEach(unit => {
              totalWeekMinutes += unit.duration_minutes || 0
            })
          })

          return (
            <div key={weekIdx} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Заголовок недели */}
              <button
                onClick={() => toggleWeek(weekIndex)}
                className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 text-left"
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{isExpanded ? '▼' : '▶'}</span>
                  <div>
                    <div className="font-semibold text-gray-900">
                      Неделя {weekIndex + 1}
                    </div>
                    <div className="text-sm text-gray-600">
                      {days.length} дней · {formatDuration(totalWeekMinutes)}
                    </div>
                  </div>
                </div>
              </button>

              {/* Содержимое недели */}
              {isExpanded && (
                <div className="p-4 space-y-3">
                  {days.map((day, dayIdx) => {
                    const dayIndex = day.day_index ?? dayIdx
                    const units = day.learning_units || []

                    // Подсчитать общее время дня
                    const totalDayMinutes = units.reduce(
                      (sum, unit) => sum + (unit.duration_minutes || 0),
                      0
                    )

                    return (
                      <div key={dayIdx} className="border-l-4 border-blue-300 pl-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-medium text-gray-900">
                            {getDayName(dayIndex)}
                          </div>
                          <div className="text-sm text-gray-600">
                            {formatDuration(totalDayMinutes)}
                          </div>
                        </div>

                        {/* Учебные единицы дня */}
                        {units.length > 0 ? (
                          <div className="space-y-2">
                            {units.map((unit, unitIdx) => {
                              const isCheckpoint = unit.is_checkpoint || unit.type === 'checkpoint'

                              return (
                                <div
                                  key={unitIdx}
                                  className={`p-3 rounded ${
                                    isCheckpoint
                                      ? 'bg-yellow-50 border border-yellow-300'
                                      : 'bg-gray-50 border border-gray-200'
                                  }`}
                                >
                                  <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2">
                                        {isCheckpoint && <span className="text-lg">📌</span>}
                                        <span className="font-medium text-sm">
                                          {unit.title || unit.id || 'Без названия'}
                                        </span>
                                      </div>
                                      <div className="text-xs text-gray-600 mt-1">
                                        {unit.type}
                                        {isCheckpoint && ' (Checkpoint)'}
                                      </div>
                                    </div>
                                    <div className="text-sm text-gray-600 ml-3">
                                      {formatDuration(unit.duration_minutes)}
                                    </div>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">Нет учебных единиц</div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
