'use client'

import { useState } from 'react'

interface InputDataEditorProps {
  inputData: Record<string, unknown> | null
  onChange: (data: Record<string, unknown> | null) => void
}

export default function InputDataEditor({ inputData, onChange }: InputDataEditorProps) {
  const [mode, setMode] = useState<'auto' | 'manual'>('auto')
  const [jsonText, setJsonText] = useState(inputData ? JSON.stringify(inputData, null, 2) : '')
  const [error, setError] = useState<string | null>(null)

  const handleModeChange = (newMode: 'auto' | 'manual') => {
    setMode(newMode)
    if (newMode === 'auto') {
      onChange(null) // null means auto-input from previous step
      setError(null)
    }
  }

  const handleJsonChange = (text: string) => {
    setJsonText(text)
    setError(null)
    try {
      const parsed = JSON.parse(text)
      onChange(parsed)
    } catch (e) {
      if (e instanceof SyntaxError) {
        setError(e.message)
      }
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <h4 className="text-sm font-medium text-gray-700">Входные данные</h4>
        <div className="flex text-xs border rounded overflow-hidden">
          <button
            onClick={() => handleModeChange('auto')}
            className={`px-2 py-1 ${mode === 'auto' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-50'}`}
          >
            Авто
          </button>
          <button
            onClick={() => handleModeChange('manual')}
            className={`px-2 py-1 ${mode === 'manual' ? 'bg-indigo-100 text-indigo-700' : 'hover:bg-gray-50'}`}
          >
            Вручную
          </button>
        </div>
      </div>

      {mode === 'auto' ? (
        <div className="text-xs text-gray-400 px-2 py-1">
          Данные будут взяты из результата предыдущего шага
        </div>
      ) : (
        <>
          <textarea
            value={jsonText}
            onChange={(e) => handleJsonChange(e.target.value)}
            className={`w-full px-3 py-2 border rounded text-sm font-mono resize-y ${
              error ? 'border-red-300 bg-red-50' : 'bg-white'
            }`}
            rows={6}
            placeholder='{"key": "value"}'
            spellCheck={false}
          />
          {error && (
            <div className="text-xs text-red-500">{error}</div>
          )}
        </>
      )}
    </div>
  )
}
