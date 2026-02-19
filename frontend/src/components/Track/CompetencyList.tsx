'use client'

import EmptySection from './EmptySection'
import { CompetencySetData, LEVEL_LABELS } from '@/types/track'

interface CompetencyListProps {
  data?: CompetencySetData
}

/** Список компетенций из шага B2. */
export default function CompetencyList({ data }: CompetencyListProps) {
  if (!data || !data.competencies?.length) {
    return <EmptySection message="Компетенции не сгенерированы" step="B2" />
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Компетенции
        </h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
          {data.competencies.length} шт.
        </span>
      </div>

      {data.competencies.map(comp => {
        const isIntegral = comp.id === data.integral_competency_id
        return (
          <div
            key={comp.id}
            className={`rounded-lg border p-5 ${
              isIntegral
                ? 'border-blue-300 bg-blue-50'
                : 'border-gray-200 bg-white'
            }`}
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <h4 className="font-semibold text-gray-900 text-sm leading-snug">
                {comp.title}
              </h4>
              <div className="flex items-center gap-2 shrink-0">
                {isIntegral && (
                  <span className="text-xs bg-blue-200 text-blue-800 px-2 py-0.5 rounded-full font-medium">
                    Интегративная
                  </span>
                )}
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  {LEVEL_LABELS[comp.level] ?? comp.level}
                </span>
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed">{comp.description}</p>
          </div>
        )
      })}
    </div>
  )
}
