'use client'

import React from 'react'
import type { ProfileFormBarrier, ProfileFormTask } from '@/types'

interface BarrierEditorProps {
  barriers: ProfileFormBarrier[]
  tasks: ProfileFormTask[]
  onChange: (barriers: ProfileFormBarrier[]) => void
  disabled?: boolean
}

let barrierCounter = 1

const BARRIER_TYPES: { value: ProfileFormBarrier['barrier_type']; label: string }[] = [
  { value: 'conceptual', label: 'Концептуальный' },
  { value: 'procedural', label: 'Процедурный' },
  { value: 'motivational', label: 'Мотивационный' },
]

export default function BarrierEditor({ barriers, tasks, onChange, disabled = false }: BarrierEditorProps) {
  const add = () => {
    onChange([
      ...barriers,
      { id: `b${barrierCounter++}`, description: '', barrier_type: 'conceptual', related_task_id: tasks[0]?.id ?? '' },
    ])
  }

  const update = (index: number, patch: Partial<ProfileFormBarrier>) => {
    onChange(barriers.map((b, i) => i === index ? { ...b, ...patch } : b))
  }

  const remove = (index: number) => {
    onChange(barriers.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-3">
      {barriers.map((barrier, i) => (
        <div key={barrier.id} className="p-3 border border-gray-200 rounded space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">ID: {barrier.id}</span>
            <button type="button" onClick={() => remove(i)} disabled={disabled}
              className="text-red-500 hover:text-red-700 text-sm disabled:opacity-40">✕ Удалить</button>
          </div>
          <input
            type="text"
            value={barrier.description}
            onChange={e => update(i, { description: e.target.value })}
            placeholder="Описание барьера..."
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Тип барьера</label>
              <select
                value={barrier.barrier_type}
                onChange={e => update(i, { barrier_type: e.target.value as ProfileFormBarrier['barrier_type'] })}
                disabled={disabled}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
              >
                {BARRIER_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Связанная задача</label>
              <select
                value={barrier.related_task_id}
                onChange={e => update(i, { related_task_id: e.target.value })}
                disabled={disabled}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
              >
                <option value="">— выбрать —</option>
                {tasks.map(t => <option key={t.id} value={t.id}>{t.description || t.id}</option>)}
              </select>
            </div>
          </div>
        </div>
      ))}
      <button type="button" onClick={add} disabled={disabled}
        className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40">
        + Добавить барьер
      </button>
    </div>
  )
}
