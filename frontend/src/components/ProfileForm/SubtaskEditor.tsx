'use client'

import React from 'react'
import type { ProfileFormSubtask, ProfileFormTask } from '@/types'
import DynamicList from './DynamicList'

interface SubtaskEditorProps {
  subtasks: ProfileFormSubtask[]
  tasks: ProfileFormTask[]
  onChange: (subtasks: ProfileFormSubtask[]) => void
  disabled?: boolean
}

let subtaskCounter = 1

export default function SubtaskEditor({ subtasks, tasks, onChange, disabled = false }: SubtaskEditorProps) {
  const add = () => {
    const parentId = tasks[0]?.id ?? ''
    onChange([
      ...subtasks,
      { id: `st${subtaskCounter++}`, description: '', parent_task_id: parentId, required_skills: [], required_knowledge: [] },
    ])
  }

  const update = (index: number, patch: Partial<ProfileFormSubtask>) => {
    onChange(subtasks.map((s, i) => i === index ? { ...s, ...patch } : s))
  }

  const remove = (index: number) => {
    onChange(subtasks.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-3">
      {subtasks.map((st, i) => (
        <div key={st.id} className="p-3 border border-gray-200 rounded space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">ID: {st.id}</span>
            <button type="button" onClick={() => remove(i)} disabled={disabled}
              className="text-red-500 hover:text-red-700 text-sm disabled:opacity-40">✕ Удалить</button>
          </div>
          <input
            type="text"
            value={st.description}
            onChange={e => update(i, { description: e.target.value })}
            placeholder="Описание подзадачи..."
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <div>
            <label className="block text-xs text-gray-500 mb-1">Родительская задача</label>
            <select
              value={st.parent_task_id}
              onChange={e => update(i, { parent_task_id: e.target.value })}
              disabled={disabled}
              className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
            >
              <option value="">— выбрать задачу —</option>
              {tasks.map(t => <option key={t.id} value={t.id}>{t.description || t.id}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Необходимые навыки</label>
            <DynamicList items={st.required_skills} onChange={items => update(i, { required_skills: items })}
              placeholder="Навык..." disabled={disabled} />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Необходимые знания</label>
            <DynamicList items={st.required_knowledge} onChange={items => update(i, { required_knowledge: items })}
              placeholder="Знание..." disabled={disabled} />
          </div>
        </div>
      ))}
      <button type="button" onClick={add} disabled={disabled}
        className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40">
        + Добавить подзадачу
      </button>
    </div>
  )
}
