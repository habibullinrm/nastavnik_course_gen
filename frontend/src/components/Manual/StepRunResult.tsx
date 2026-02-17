'use client'

import type { StepRunResponse } from '@/types/manual'
import JsonViewer from './JsonViewer'
import UserRating from './UserRating'
import AutoEvaluation from './AutoEvaluation'

function LLMJudgeResult({ evaluation }: { evaluation: Record<string, unknown> }) {
  const score = Number(evaluation.score) || 0
  const summary = String(evaluation.summary || '')
  const strengths = (evaluation.strengths as string[]) || []
  const problems = (evaluation.problems as string[]) || []
  const suggestions = (evaluation.suggestions as string[]) || []
  const reasoning = String(evaluation.reasoning || '')

  const scoreColor = score >= 7 ? 'text-green-700 bg-green-50 border-green-200'
    : score >= 5 ? 'text-yellow-700 bg-yellow-50 border-yellow-200'
    : 'text-red-700 bg-red-50 border-red-200'

  return (
    <div className="p-3 bg-purple-50 border border-purple-200 rounded text-sm space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium text-purple-800">LLM Judge</span>
        <span className={`px-2 py-0.5 rounded border text-xs font-bold ${scoreColor}`}>
          {score}/10
        </span>
      </div>

      {summary && <p className="text-purple-700">{summary}</p>}

      {strengths.length > 0 && (
        <div>
          <div className="text-xs font-medium text-green-700 mb-0.5">Сильные стороны:</div>
          <ul className="list-none space-y-0.5">
            {strengths.map((s, i) => (
              <li key={i} className="text-xs text-green-600 pl-2">+ {s}</li>
            ))}
          </ul>
        </div>
      )}

      {problems.length > 0 && (
        <div>
          <div className="text-xs font-medium text-red-700 mb-0.5">Проблемы:</div>
          <ul className="list-none space-y-0.5">
            {problems.map((p, i) => (
              <li key={i} className="text-xs text-red-600 pl-2">- {p}</li>
            ))}
          </ul>
        </div>
      )}

      {suggestions.length > 0 && (
        <div>
          <div className="text-xs font-medium text-blue-700 mb-0.5">Рекомендации:</div>
          <ul className="list-none space-y-0.5">
            {suggestions.map((s, i) => (
              <li key={i} className="text-xs text-blue-600 pl-2">* {s}</li>
            ))}
          </ul>
        </div>
      )}

      {reasoning && (
        <details className="text-xs">
          <summary className="cursor-pointer text-purple-500 hover:text-purple-700">
            Подробное обоснование
          </summary>
          <p className="mt-1 text-purple-600 whitespace-pre-wrap">{reasoning}</p>
        </details>
      )}
    </div>
  )
}

interface StepRunResultProps {
  run: StepRunResponse | null
  onSaveRating: (rating: number | null, notes: string | null) => void
  onRequestJudge: () => void
  judgeLoading?: boolean
}

export default function StepRunResult({ run, onSaveRating, onRequestJudge, judgeLoading }: StepRunResultProps) {
  if (!run) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        Запустите шаг для просмотра результатов
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">
          Запуск #{run.run_number} — <span className={
            run.status === 'completed' ? 'text-green-600' :
            run.status === 'failed' ? 'text-red-600' :
            run.status === 'running' ? 'text-blue-600' : 'text-gray-500'
          }>{run.status}</span>
        </h3>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {run.tokens_used != null && <span>Токены: {run.tokens_used}</span>}
          {run.duration_ms != null && <span>Время: {(run.duration_ms / 1000).toFixed(1)}с</span>}
        </div>
      </div>

      {/* Error */}
      {run.parse_error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {run.parse_error}
        </div>
      )}

      {/* Rendered prompt */}
      <JsonViewer data={run.rendered_prompt} title="Рендеренный промпт" maxHeight="200px" />

      {/* Input data */}
      <JsonViewer data={run.input_data} title="Входные данные" />

      {/* Raw response */}
      {run.raw_response && (
        <JsonViewer data={run.raw_response} title="Сырой ответ LLM" />
      )}

      {/* Parsed result */}
      <JsonViewer data={run.parsed_result} title="Разобранный результат" defaultExpanded />

      {/* Processors */}
      {run.preprocessor_results && run.preprocessor_results.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Пре-процессоры</h4>
          {run.preprocessor_results.map((p, i) => (
            <div key={i} className={`text-sm px-2 py-1 rounded ${p.passed ? 'bg-green-50' : 'bg-red-50'}`}>
              {p.passed ? '✓' : '✗'} {p.name}: {p.message || p.error}
            </div>
          ))}
        </div>
      )}
      {run.postprocessor_results && run.postprocessor_results.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Пост-процессоры</h4>
          {run.postprocessor_results.map((p, i) => (
            <div key={i} className={`text-sm px-2 py-1 rounded ${p.passed ? 'bg-green-50' : 'bg-red-50'}`}>
              {p.passed ? '✓' : '✗'} {p.name}: {p.message || p.error}
            </div>
          ))}
        </div>
      )}

      {/* Auto evaluation */}
      <AutoEvaluation evaluation={run.auto_evaluation} />

      {/* LLM Judge */}
      <div className="space-y-2">
        {run.llm_judge_evaluation ? (
          <LLMJudgeResult evaluation={run.llm_judge_evaluation as Record<string, unknown>} />
        ) : (
          <button
            onClick={onRequestJudge}
            disabled={judgeLoading || !run.parsed_result}
            className="px-3 py-1.5 text-sm border border-purple-300 text-purple-700 rounded hover:bg-purple-50 disabled:opacity-50"
          >
            {judgeLoading ? 'Запрос...' : 'Запросить LLM-Judge'}
          </button>
        )}
      </div>

      {/* Rating */}
      <UserRating
        rating={run.user_rating}
        notes={run.user_notes}
        onSave={onSaveRating}
      />
    </div>
  )
}
