'use client'

import React from 'react'
import type { ProfileFormScheduleDay } from '@/types'

const DAYS: { value: ProfileFormScheduleDay['day_of_week']; label: string }[] = [
  { value: 'monday', label: 'Пн' },
  { value: 'tuesday', label: 'Вт' },
  { value: 'wednesday', label: 'Ср' },
  { value: 'thursday', label: 'Чт' },
  { value: 'friday', label: 'Пт' },
  { value: 'saturday', label: 'Сб' },
  { value: 'sunday', label: 'Вс' },
]

interface ScheduleEditorProps {
  schedule: ProfileFormScheduleDay[]
  onChange: (schedule: ProfileFormScheduleDay[]) => void
  disabled?: boolean
}

export default function ScheduleEditor({ schedule, onChange, disabled = false }: ScheduleEditorProps) {
  const getMinutes = (day: ProfileFormScheduleDay['day_of_week']): number =>
    schedule.find(s => s.day_of_week === day)?.available_minutes ?? 0

  const setMinutes = (day: ProfileFormScheduleDay['day_of_week'], minutes: number) => {
    const existing = schedule.find(s => s.day_of_week === day)
    if (minutes === 0) {
      onChange(schedule.filter(s => s.day_of_week !== day))
    } else if (existing) {
      onChange(schedule.map(s => s.day_of_week === day ? { ...s, available_minutes: minutes } : s))
    } else {
      onChange([...schedule, { day_of_week: day, available_minutes: minutes }])
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            {DAYS.map(d => (
              <th key={d.value} className="px-2 py-1 text-center text-gray-600 font-medium border-b border-gray-200">
                {d.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {DAYS.map(d => (
              <td key={d.value} className="px-1 py-2 text-center">
                <input
                  type="number"
                  min={0}
                  max={480}
                  step={10}
                  value={getMinutes(d.value)}
                  onChange={e => setMinutes(d.value, parseInt(e.target.value, 10) || 0)}
                  disabled={disabled}
                  className="w-16 px-1 py-1 border border-gray-300 rounded text-center text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100"
                  placeholder="мин"
                />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
      <p className="text-xs text-gray-400 mt-1">Минуты на каждый день (0 = выходной)</p>
    </div>
  )
}
