'use client'

import React from 'react'
import type { ProfileFormSuccessCriterion } from '@/types'

interface CriterionEditorProps {
  criteria: ProfileFormSuccessCriterion[]
  onChange: (criteria: ProfileFormSuccessCriterion[]) => void
  disabled?: boolean
}

let criterionCounter = 1

export default function CriterionEditor({ criteria, onChange, disabled = false }: CriterionEditorProps) {
  const add = () => {
    onChange([...criteria, { id: `sc${criterionCounter++}`, description: '', metric: '', measurable: true }])
  }

  const update = (index: number, patch: Partial<ProfileFormSuccessCriterion>) => {
    onChange(criteria.map((c, i) => i === index ? { ...c, ...patch } : c))
  }

  const remove = (index: number) => {
    onChange(criteria.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-3">
      {criteria.map((c, i) => (
        <div key={c.id} className="p-3 border border-gray-200 rounded space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">ID: {c.id}</span>
            <button type="button" onClick={() => remove(i)} disabled={disabled}
              className="text-red-500 hover:text-red-700 text-sm disabled:opacity-40">✕ Удалить</button>
          </div>
          <input
            type="text"
            value={c.description}
            onChange={e => update(i, { description: e.target.value })}
            placeholder="Описание критерия успеха..."
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <input
            type="text"
            value={c.metric}
            onChange={e => update(i, { metric: e.target.value })}
            placeholder="Метрика (напр. accuracy >= 0.8)..."
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={c.measurable}
              onChange={e => update(i, { measurable: e.target.checked })}
              disabled={disabled}
              className="w-4 h-4"
            />
            Измеримый критерий
          </label>
        </div>
      ))}
      <button type="button" onClick={add} disabled={disabled}
        className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40">
        + Добавить критерий
      </button>
    </div>
  )
}
