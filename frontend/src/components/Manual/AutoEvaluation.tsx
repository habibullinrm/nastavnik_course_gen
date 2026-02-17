'use client'

interface AutoEvaluationProps {
  evaluation: Record<string, unknown> | null
}

export default function AutoEvaluation({ evaluation }: AutoEvaluationProps) {
  if (!evaluation) return null

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">Авто-оценка</h4>
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(evaluation).map(([key, value]) => (
          <div key={key} className="flex items-center gap-2 text-sm">
            <span className="text-gray-500">{key}:</span>
            <span className={
              value === true ? 'text-green-600 font-medium' :
              value === false ? 'text-red-600 font-medium' :
              'text-gray-900'
            }>
              {value === true ? '✓' : value === false ? '✗' : String(value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
