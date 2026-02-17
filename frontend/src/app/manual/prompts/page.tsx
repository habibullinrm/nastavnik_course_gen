'use client'

import { useState, useEffect } from 'react'
import type { PromptVersion, PromptStepSummary } from '@/types/manual'
import { STEP_NAMES, STEP_DESCRIPTIONS } from '@/types/manual'
import { listPrompts, getPromptVersions, loadBaselines } from '@/services/manualApi'

export default function PromptsPage() {
  const [steps, setSteps] = useState<PromptStepSummary[]>([])
  const [selectedStep, setSelectedStep] = useState<string | null>(null)
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    setLoading(true)
    try {
      const data = await listPrompts()
      setSteps(data.steps)
    } catch (e) {
      console.error('Failed to load prompts:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleStepSelect = async (stepName: string) => {
    setSelectedStep(stepName)
    try {
      const data = await getPromptVersions(stepName)
      setVersions(data)
      if (data.length > 0) setSelectedVersion(data[0])
    } catch (e) {
      console.error('Failed to load versions:', e)
    }
  }

  const handleLoadBaselines = async () => {
    try {
      await loadBaselines()
      await load()
      alert('Baselines загружены')
    } catch (e) {
      console.error('Failed to load baselines:', e)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Версии промптов</h1>
        <button
          onClick={handleLoadBaselines}
          className="px-4 py-2 text-sm border rounded-lg hover:bg-gray-50"
        >
          Загрузить baseline
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Загрузка...</div>
      ) : (
        <div className="grid grid-cols-12 gap-4">
          {/* Steps list */}
          <div className="col-span-3 space-y-1">
            {STEP_NAMES.map(step => {
              const info = steps.find(s => s.step_name === step)
              return (
                <button
                  key={step}
                  onClick={() => handleStepSelect(step)}
                  className={`w-full text-left px-3 py-2 rounded text-sm ${
                    step === selectedStep
                      ? 'bg-indigo-50 border border-indigo-200'
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className="font-medium">{step.split('_')[0]}</div>
                  <div className="text-xs text-gray-400">
                    {STEP_DESCRIPTIONS[step]}
                    {info && ` (v${info.latest_version})`}
                  </div>
                </button>
              )
            })}
          </div>

          {/* Version list */}
          <div className="col-span-3 space-y-1">
            {versions.map(v => (
              <button
                key={v.id}
                onClick={() => setSelectedVersion(v)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${
                  v.id === selectedVersion?.id
                    ? 'bg-indigo-50 border border-indigo-200'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">v{v.version}</span>
                  {v.is_baseline && <span className="text-xs text-blue-500">baseline</span>}
                </div>
                {v.change_description && (
                  <div className="text-xs text-gray-400">{v.change_description}</div>
                )}
                <div className="text-xs text-gray-300">
                  {new Date(v.created_at).toLocaleString('ru')}
                </div>
              </button>
            ))}
          </div>

          {/* Prompt text */}
          <div className="col-span-6">
            {selectedVersion ? (
              <pre className="p-4 bg-gray-900 text-green-400 rounded-lg text-xs overflow-auto max-h-[600px]">
                {selectedVersion.prompt_text}
              </pre>
            ) : (
              <div className="text-center py-8 text-gray-400">
                Выберите шаг и версию
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
