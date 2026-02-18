'use client'

import React from 'react'

interface MultiCheckboxProps {
  options: { value: string; label: string }[]
  selected: string[]
  onChange: (selected: string[]) => void
  disabled?: boolean
}

export default function MultiCheckbox({ options, selected, onChange, disabled = false }: MultiCheckboxProps) {
  const toggle = (value: string) => {
    if (selected.includes(value)) {
      onChange(selected.filter(v => v !== value))
    } else {
      onChange([...selected, value])
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {options.map(opt => {
        const checked = selected.includes(opt.value)
        return (
          <label
            key={opt.value}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border cursor-pointer text-sm select-none transition-colors ${
              checked
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input
              type="checkbox"
              className="sr-only"
              checked={checked}
              onChange={() => !disabled && toggle(opt.value)}
              disabled={disabled}
            />
            {checked && <span>✓</span>}
            {opt.label}
          </label>
        )
      })}
    </div>
  )
}
