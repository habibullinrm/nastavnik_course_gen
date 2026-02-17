'use client'

import { useState, useEffect } from 'react'
import type { ProcessorInfo, ProcessorConfigItem } from '@/types/manual'
import { listProcessors, getProcessorConfig, setProcessorConfig } from '@/services/manualApi'

interface ProcessorConfigProps {
  sessionId: string
  stepName: string
}

export default function ProcessorConfig({ sessionId, stepName }: ProcessorConfigProps) {
  const [available, setAvailable] = useState<ProcessorInfo[]>([])
  const [configs, setConfigs] = useState<ProcessorConfigItem[]>([])
  const [saving, setSaving] = useState(false)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, stepName])

  const loadData = async () => {
    try {
      const [procs, cfg] = await Promise.all([
        listProcessors(),
        getProcessorConfig(sessionId, stepName),
      ])
      setAvailable(procs.filter(p => p.applicable_steps.includes(stepName)))
      setConfigs(cfg.processors)
    } catch (e) {
      console.error('Failed to load processors:', e)
    }
  }

  const handleToggle = (procName: string, procType: string) => {
    const existing = configs.find(c => c.processor_name === procName)
    if (existing) {
      setConfigs(configs.map(c =>
        c.processor_name === procName ? { ...c, enabled: !c.enabled } : c
      ))
    } else {
      setConfigs([...configs, {
        processor_name: procName,
        processor_type: procType,
        execution_order: configs.length + 1,
        enabled: true,
        config_params: null,
      }])
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const result = await setProcessorConfig(sessionId, stepName, configs)
      setConfigs(result.processors)
    } catch (e) {
      console.error('Failed to save processor config:', e)
    } finally {
      setSaving(false)
    }
  }

  const preProcessors = available.filter(p => p.type === 'pre')
  const postProcessors = available.filter(p => p.type === 'post')

  const isEnabled = (name: string) => {
    const cfg = configs.find(c => c.processor_name === name)
    return cfg?.enabled ?? false
  }

  if (available.length === 0 && !expanded) {
    return (
      <div className="text-xs text-gray-400">
        Нет доступных обработчиков для этого шага
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-sm font-medium text-gray-700 flex items-center gap-1"
      >
        <span>{expanded ? '▾' : '▸'}</span>
        Обработчики ({configs.filter(c => c.enabled).length}/{available.length})
      </button>

      {expanded && (
        <div className="space-y-3">
          {preProcessors.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Пре-процессоры</div>
              {preProcessors.map(p => (
                <label key={p.name} className="flex items-center gap-2 text-sm py-0.5">
                  <input
                    type="checkbox"
                    checked={isEnabled(p.name)}
                    onChange={() => handleToggle(p.name, 'pre')}
                  />
                  <span>{p.name}</span>
                  <span className="text-xs text-gray-400">{p.description}</span>
                </label>
              ))}
            </div>
          )}

          {postProcessors.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Пост-процессоры</div>
              {postProcessors.map(p => (
                <label key={p.name} className="flex items-center gap-2 text-sm py-0.5">
                  <input
                    type="checkbox"
                    checked={isEnabled(p.name)}
                    onChange={() => handleToggle(p.name, 'post')}
                  />
                  <span>{p.name}</span>
                  <span className="text-xs text-gray-400">{p.description}</span>
                </label>
              ))}
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="px-3 py-1 text-xs bg-gray-100 border rounded hover:bg-gray-200 disabled:opacity-50"
          >
            {saving ? 'Сохранение...' : 'Сохранить конфигурацию'}
          </button>
        </div>
      )}
    </div>
  )
}
