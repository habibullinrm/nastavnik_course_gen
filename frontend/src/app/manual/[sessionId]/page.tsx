'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import type { ManualSession, StepRunResponse, StepRunSummary, StepStatus } from '@/types/manual'
import { STEP_NAMES } from '@/types/manual'
import {
  getSession, runStep, getStepsStatus, getStepRuns, getRunDetail,
  updateRunRating, requestLLMJudge,
} from '@/services/manualApi'
import StepTabs from '@/components/Manual/StepTabs'
import PromptEditor from '@/components/Manual/PromptEditor'
import StepRunResult from '@/components/Manual/StepRunResult'
import RunHistory from '@/components/Manual/RunHistory'
import JsonViewer from '@/components/Manual/JsonViewer'
import ProcessorConfig from '@/components/Manual/ProcessorConfig'
import InputDataEditor from '@/components/Manual/InputDataEditor'

export default function ManualWorkspacePage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [session, setSession] = useState<ManualSession | null>(null)
  const [activeStep, setActiveStep] = useState<string>(STEP_NAMES[0])
  const [stepStatuses, setStepStatuses] = useState<Record<string, StepStatus>>({})
  const [currentRun, setCurrentRun] = useState<StepRunResponse | null>(null)
  const [runHistory, setRunHistory] = useState<StepRunSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [judgeLoading, setJudgeLoading] = useState(false)

  // Prompt state
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null)
  const [promptText, setPromptText] = useState('')

  // Input data
  const [customInputData, setCustomInputData] = useState<Record<string, unknown> | null>(null)

  // LLM params
  const [temperature, setTemperature] = useState(0.3)
  const [maxTokens, setMaxTokens] = useState(8000)
  const [useMock, setUseMock] = useState(true)

  const loadSession = useCallback(async () => {
    try {
      const [sess, statuses] = await Promise.all([
        getSession(sessionId),
        getStepsStatus(sessionId),
      ])
      setSession(sess)
      setStepStatuses(statuses.steps)
    } catch (e) {
      console.error('Failed to load session:', e)
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  const loadStepData = useCallback(async () => {
    try {
      const runs = await getStepRuns(sessionId, activeStep)
      setRunHistory(runs)
      if (runs.length > 0) {
        const detail = await getRunDetail(sessionId, runs[0].id)
        setCurrentRun(detail)
      } else {
        setCurrentRun(null)
      }
    } catch (e) {
      console.error('Failed to load step data:', e)
    }
  }, [sessionId, activeStep])

  useEffect(() => { loadSession() }, [loadSession])
  useEffect(() => { loadStepData() }, [loadStepData])

  // Reset prompt selection when switching steps
  useEffect(() => {
    setSelectedPromptId(null)
    setPromptText('')
    setCustomInputData(null)
  }, [activeStep])

  const handleRunStep = async () => {
    setRunning(true)
    try {
      const result = await runStep(sessionId, activeStep, {
        prompt_version_id: selectedPromptId || undefined,
        // custom_prompt только если нет выбранной версии (ручной ввод)
        custom_prompt: selectedPromptId ? undefined : (promptText || undefined),
        input_data: customInputData || undefined,
        llm_params: { temperature, max_tokens: maxTokens },
        use_mock: useMock,
      })
      setCurrentRun(result)
      await loadStepData()
      await loadSession() // refresh statuses
    } catch (e) {
      console.error('Step run failed:', e)
      alert(`Ошибка: ${e}`)
    } finally {
      setRunning(false)
    }
  }

  const handleSaveRating = async (rating: number | null, notes: string | null) => {
    if (!currentRun) return
    try {
      const updated = await updateRunRating(sessionId, currentRun.id, rating, notes || undefined)
      setCurrentRun(updated)
      await loadStepData()
    } catch (e) {
      console.error('Failed to save rating:', e)
    }
  }

  const handleRequestJudge = async () => {
    if (!currentRun) return
    setJudgeLoading(true)
    try {
      const updated = await requestLLMJudge(sessionId, currentRun.id, useMock)
      setCurrentRun(updated)
    } catch (e) {
      console.error('LLM Judge failed:', e)
    } finally {
      setJudgeLoading(false)
    }
  }

  const handleRunSelect = async (runId: string) => {
    try {
      const detail = await getRunDetail(sessionId, runId)
      setCurrentRun(detail)
    } catch (e) {
      console.error('Failed to load run:', e)
    }
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Загрузка...</div>
  }

  if (!session) {
    return <div className="text-center py-8 text-red-500">Сессия не найдена</div>
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/manual" className="text-gray-400 hover:text-gray-600">
            ← Сессии
          </Link>
          <h1 className="text-xl font-bold">{session.name}</h1>
          <span className={`px-2 py-0.5 text-xs rounded-full ${
            session.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
          }`}>
            {session.status}
          </span>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/manual/${sessionId}/profile`}
            className="px-3 py-1.5 text-sm border rounded hover:bg-gray-50"
          >
            Редактировать профиль
          </Link>
          <Link
            href="/manual/prompts"
            className="px-3 py-1.5 text-sm border rounded hover:bg-gray-50"
          >
            Промпты
          </Link>
        </div>
      </div>

      {/* Step Tabs */}
      <StepTabs
        activeStep={activeStep}
        onStepChange={setActiveStep}
        stepStatuses={stepStatuses}
      />

      {/* Main Content */}
      <div className="grid grid-cols-2 gap-4">
        {/* Left: Configuration */}
        <div className="space-y-4">
          {/* Prompt Editor */}
          <div className="border rounded-lg p-4 bg-white">
            <PromptEditor
              stepName={activeStep}
              selectedVersionId={selectedPromptId}
              onVersionSelect={(id, text) => {
                setSelectedPromptId(id)
                setPromptText(text)
              }}
            />
          </div>

          {/* Input Data Editor */}
          <div className="border rounded-lg p-4 bg-white">
            <InputDataEditor
              inputData={customInputData}
              onChange={setCustomInputData}
            />
          </div>

          {/* Processor Config */}
          <div className="border rounded-lg p-4 bg-white">
            <ProcessorConfig
              sessionId={sessionId}
              stepName={activeStep}
            />
          </div>

          {/* LLM Params */}
          <div className="border rounded-lg p-4 bg-white space-y-3">
            <h3 className="text-sm font-medium text-gray-700">Параметры LLM</h3>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Temperature</label>
                <input
                  type="number"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  min={0} max={2} step={0.1}
                  className="w-full border rounded px-2 py-1 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Max Tokens</label>
                <input
                  type="number"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  min={100} max={32000} step={100}
                  className="w-full border rounded px-2 py-1 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Режим</label>
                <label className="flex items-center gap-2 text-sm mt-1">
                  <input
                    type="checkbox"
                    checked={useMock}
                    onChange={(e) => setUseMock(e.target.checked)}
                  />
                  Mock
                </label>
              </div>
            </div>

            <button
              onClick={handleRunStep}
              disabled={running}
              className="w-full py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {running ? 'Выполнение...' : 'ЗАПУСТИТЬ ШАГ'}
            </button>
          </div>

          {/* Profile snapshot preview */}
          <div className="border rounded-lg p-4 bg-white">
            <JsonViewer
              data={session.profile_snapshot}
              title="Профиль (snapshot)"
              maxHeight="200px"
            />
          </div>
        </div>

        {/* Right: Results */}
        <div className="space-y-4">
          {/* Current run result */}
          <div className="border rounded-lg p-4 bg-white min-h-[300px]">
            <StepRunResult
              run={currentRun}
              onSaveRating={handleSaveRating}
              onRequestJudge={handleRequestJudge}
              judgeLoading={judgeLoading}
            />
          </div>

          {/* Run history */}
          <div className="border rounded-lg p-4 bg-white">
            <RunHistory
              runs={runHistory}
              selectedRunId={currentRun?.id || null}
              onRunSelect={handleRunSelect}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
