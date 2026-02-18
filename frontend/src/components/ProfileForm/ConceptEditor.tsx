'use client'

import React from 'react'
import type { ProfileFormConcept } from '@/types'

interface ConceptEditorProps {
  concepts: ProfileFormConcept[]
  onChange: (concepts: ProfileFormConcept[]) => void
  disabled?: boolean
}

let conceptCounter = 1

export default function ConceptEditor({ concepts, onChange, disabled = false }: ConceptEditorProps) {
  const add = () => {
    onChange([...concepts, { id: `c${conceptCounter++}`, term: '', confusion_description: '' }])
  }

  const update = (index: number, patch: Partial<ProfileFormConcept>) => {
    onChange(concepts.map((c, i) => i === index ? { ...c, ...patch } : c))
  }

  const remove = (index: number) => {
    onChange(concepts.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-3">
      {concepts.map((concept, i) => (
        <div key={concept.id} className="p-3 border border-gray-200 rounded space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400 font-mono">ID: {concept.id}</span>
            <button type="button" onClick={() => remove(i)} disabled={disabled}
              className="text-red-500 hover:text-red-700 text-sm disabled:opacity-40">✕ Удалить</button>
          </div>
          <input
            type="text"
            value={concept.term}
            onChange={e => update(i, { term: e.target.value })}
            placeholder="Термин / понятие..."
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100"
          />
          <textarea
            value={concept.confusion_description}
            onChange={e => update(i, { confusion_description: e.target.value })}
            placeholder="В чём возникает затруднение?"
            rows={2}
            disabled={disabled}
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:bg-gray-100 resize-none"
          />
        </div>
      ))}
      <button type="button" onClick={add} disabled={disabled}
        className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-40">
        + Добавить понятие
      </button>
    </div>
  )
}
