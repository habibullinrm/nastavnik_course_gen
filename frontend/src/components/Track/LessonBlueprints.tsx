'use client'

import { useState } from 'react'
import EmptySection from './EmptySection'
import { LessonBlueprintsData } from '@/types/track'

interface LessonBlueprintsProps {
  data?: LessonBlueprintsData
}

function StringList({ items, label }: { items: string[]; label: string }) {
  if (!items?.length) return null
  return (
    <div className="mb-3">
      <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
        {label}
      </h5>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-gray-700 flex gap-2">
            <span className="text-gray-400 shrink-0">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function BlueprintCard({ blueprint, index }: { blueprint: LessonBlueprintsData['blueprints'][0]; index: number }) {
  const [open, setOpen] = useState(index === 0)

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-start gap-4 p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="shrink-0 w-7 h-7 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-800 line-clamp-2">
            {blueprint.problem_formulation?.problem_statement?.slice(0, 120)}
            {(blueprint.problem_formulation?.problem_statement?.length ?? 0) > 120 && '...'}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">Кластер: {blueprint.cluster_id}</p>
        </div>
        <span className="text-gray-400 text-xs mt-1 shrink-0">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="border-t border-gray-100 p-4 space-y-4">
          {/* Формулировка проблемы */}
          <div>
            <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
              Проблемная ситуация
            </h5>
            <p className="text-sm text-gray-700 leading-relaxed bg-orange-50 rounded p-3 border border-orange-100">
              {blueprint.problem_formulation?.problem_statement}
            </p>
          </div>

          {/* Гипотезы */}
          {(blueprint.problem_formulation?.expected_hypotheses?.length ?? 0) > 0 && (
            <div>
              <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                Ожидаемые гипотезы
              </h5>
              <ul className="space-y-1">
                {blueprint.problem_formulation.expected_hypotheses.map((h, i) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2">
                    <span className="text-orange-400 font-bold shrink-0">{i + 1}.</span>
                    <span className="italic">{h}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <StringList items={blueprint.knowledge_infusions} label="Инъекции знаний (КИ)" />
          <StringList items={blueprint.practice_tasks} label="Практические задания (ПМ)" />
          <StringList items={blueprint.contradictions} label="Противоречия" />
          <StringList items={blueprint.synthesis_tasks} label="Задания на синтез" />
          <StringList items={blueprint.reflection_questions} label="Вопросы для рефлексии" />
        </div>
      )}
    </div>
  )
}

/** PBL-сценарии из шага B6: список lesson_blueprints. */
export default function LessonBlueprints({ data }: LessonBlueprintsProps) {
  if (!data || !data.blueprints?.length) {
    return <EmptySection message="PBL-сценарии не сгенерированы" step="B6" />
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          PBL-сценарии
        </h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
          {data.blueprints.length} шт.
        </span>
      </div>

      {data.blueprints.map((bp, i) => (
        <BlueprintCard key={bp.id} blueprint={bp} index={i} />
      ))}
    </div>
  )
}
