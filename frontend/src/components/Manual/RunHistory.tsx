'use client'

import type { StepRunSummary } from '@/types/manual'

interface RunHistoryProps {
  runs: StepRunSummary[]
  selectedRunId: string | null
  onRunSelect: (runId: string) => void
}

export default function RunHistory({ runs, selectedRunId, onRunSelect }: RunHistoryProps) {
  if (runs.length === 0) {
    return <p className="text-sm text-gray-400 italic">Нет запусков</p>
  }

  return (
    <div className="space-y-1">
      <h4 className="text-sm font-medium text-gray-700">История запусков</h4>
      {runs.map((run) => (
        <button
          key={run.id}
          onClick={() => onRunSelect(run.id)}
          className={`w-full text-left px-3 py-2 rounded text-sm flex items-center justify-between
            ${run.id === selectedRunId ? 'bg-indigo-50 border border-indigo-200' : 'hover:bg-gray-50 border border-transparent'}
          `}
        >
          <div className="flex items-center gap-2">
            <span className={`inline-block w-2 h-2 rounded-full ${
              run.status === 'completed' ? 'bg-green-500' :
              run.status === 'failed' ? 'bg-red-500' :
              run.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`} />
            <span>#{run.run_number}</span>
            <span className="text-gray-400">{run.status}</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-gray-400">
            {run.duration_ms != null && <span>{(run.duration_ms / 1000).toFixed(1)}s</span>}
            {run.tokens_used != null && <span>{run.tokens_used} tok</span>}
            {run.user_rating != null && <span className="text-yellow-500">{'★'.repeat(run.user_rating)}</span>}
          </div>
        </button>
      ))}
    </div>
  )
}
