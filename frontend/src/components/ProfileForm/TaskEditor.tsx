'use client'

import React, { useState } from 'react'
import type { ProfileFormTask } from '@/types'

interface TaskEditorProps {
  tasks: ProfileFormTask[]
  taskHierarchy: ProfileFormTask[]
  easiestTaskId: string
  peakTaskId: string
  onTasksChange: (tasks: ProfileFormTask[]) => void
  onHierarchyChange: (hierarchy: ProfileFormTask[]) => void
  onEasiestChange: (id: string) => void
  onPeakChange: (id: string) => void
  disabled?: boolean
}

let taskCounter = 1

function newTask(): ProfileFormTask {
  return { id: `t${taskCounter++}`, description: '', complexity_rank: 1 }
}

export default function TaskEditor({
  tasks,
  taskHierarchy,
  easiestTaskId,
  peakTaskId,
  onTasksChange,
  onHierarchyChange,
  onEasiestChange,
  onPeakChange,
  disabled = false,
}: TaskEditorProps) {
  const [dragIdx, setDragIdx] = useState<number | null>(null)

  const addTask = () => {
    const task = newTask()
    onTasksChange([...tasks, task])
    onHierarchyChange([...taskHierarchy, { ...task, complexity_rank: taskHierarchy.length + 1 }])
  }

  const updateTask = (index: number, patch: Partial<ProfileFormTask>) => {
    const oldId = tasks[index].id
    const next = tasks.map((t, i) => i === index ? { ...t, ...patch } : t)
    onTasksChange(next)
    const newId = patch.id ?? oldId
    onHierarchyChange(taskHierarchy.map(h => h.id === oldId ? { ...h, ...patch, id: newId } : h))
  }

  const removeTask = (index: number) => {
    const removed = tasks[index]
    onTasksChange(tasks.filter((_, i) => i !== index))
    onHierarchyChange(taskHierarchy.filter(h => h.id !== removed.id))
    if (easiestTaskId === removed.id) onEasiestChange('')
    if (peakTaskId === removed.id) onPeakChange('')
  }

  const handleDragStart = (i: number) => setDragIdx(i)
  const handleDrop = (i: number) => {
    if (dragIdx === null || dragIdx === i) return
    const arr = [...taskHierarchy]
    const [moved] = arr.splice(dragIdx, 1)
    arr.splice(i, 0, moved)
    onHierarchyChange(arr.map((t, idx) => ({ ...t, complexity_rank: idx + 1 })))
    setDragIdx(null)
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {tasks.map((task, i) => (
          <div key={task.id} className="flex items-center gap-2 p-2 border border-gray-200 rounded">
            <input
              type="text"
              value={task.description}
              onChange={e => updateTask(i, { description: e.target.value })}
              placeholder="Описание задачи..."
              disabled={disabled}
              className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
            />
            <span className="text-xs text-gray-400 whitespace-nowrap">ID: {task.id}</span>
            <button
              type="button"
              onClick={() => removeTask(i)}
              disabled={disabled}
              className="text-red-500 hover:text-red-700 text-sm px-1 disabled:opacity-40"
            >✕</button>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={addTask}
        disabled={disabled}
        className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40"
      >
        + Добавить задачу
      </button>

      {tasks.length > 0 && (
        <>
          <div>
            <p className="text-xs text-gray-500 mb-1">Перетащите для изменения порядка сложности (1 = проще):</p>
            <div className="space-y-1">
              {taskHierarchy.map((task, i) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={() => handleDragStart(i)}
                  onDragOver={e => e.preventDefault()}
                  onDrop={() => handleDrop(i)}
                  className={`flex items-center gap-2 px-3 py-1.5 border rounded cursor-move text-sm ${
                    dragIdx === i ? 'border-blue-400 bg-blue-50' : 'border-gray-200 bg-white'
                  }`}
                >
                  <span className="text-gray-400">⠿</span>
                  <span className="text-gray-500 w-5 text-xs">{task.complexity_rank}.</span>
                  <span className="flex-1 truncate text-gray-700">{task.description || '(без описания)'}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Самая простая задача 🟢</label>
              <select
                value={easiestTaskId}
                onChange={e => onEasiestChange(e.target.value)}
                disabled={disabled}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
              >
                <option value="">— выбрать —</option>
                {tasks.map(t => <option key={t.id} value={t.id}>{t.description || t.id}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Вершина мастерства 🔴</label>
              <select
                value={peakTaskId}
                onChange={e => onPeakChange(e.target.value)}
                disabled={disabled}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
              >
                <option value="">— выбрать —</option>
                {tasks.map(t => <option key={t.id} value={t.id}>{t.description || t.id}</option>)}
              </select>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
