'use client'

import React, { useState } from 'react'

interface DynamicListProps {
  items: string[]
  onChange: (items: string[]) => void
  placeholder?: string
  addLabel?: string
  disabled?: boolean
}

export default function DynamicList({
  items,
  onChange,
  placeholder = 'Введите значение...',
  addLabel = '+ Добавить',
  disabled = false,
}: DynamicListProps) {
  const [newValue, setNewValue] = useState('')

  const handleAdd = () => {
    const trimmed = newValue.trim()
    if (!trimmed) return
    onChange([...items, trimmed])
    setNewValue('')
  }

  const handleRemove = (index: number) => {
    onChange(items.filter((_, i) => i !== index))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }

  const handleEdit = (index: number, value: string) => {
    const next = [...items]
    next[index] = value
    onChange(next)
  }

  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="flex items-center gap-2">
          <input
            type="text"
            value={item}
            onChange={e => handleEdit(i, e.target.value)}
            disabled={disabled}
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <button
            type="button"
            onClick={() => handleRemove(i)}
            disabled={disabled}
            className="text-red-500 hover:text-red-700 text-sm px-2 disabled:opacity-40"
            title="Удалить"
          >
            ✕
          </button>
        </div>
      ))}
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={newValue}
          onChange={e => setNewValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100"
        />
        <button
          type="button"
          onClick={handleAdd}
          disabled={disabled || !newValue.trim()}
          className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {addLabel}
        </button>
      </div>
    </div>
  )
}
