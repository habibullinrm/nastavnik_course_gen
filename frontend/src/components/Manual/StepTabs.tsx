'use client'

import { STEP_NAMES, STEP_SHORT_NAMES, STEP_DESCRIPTIONS } from '@/types/manual'
import type { StepStatus } from '@/types/manual'

interface StepTabsProps {
  activeStep: string
  onStepChange: (step: string) => void
  stepStatuses: Record<string, StepStatus>
}

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-green-100 text-green-800 border-green-300',
  running: 'bg-blue-100 text-blue-800 border-blue-300 animate-pulse',
  failed: 'bg-red-100 text-red-800 border-red-300',
  pending: 'bg-gray-100 text-gray-500 border-gray-300',
}

const STATUS_ICONS: Record<string, string> = {
  completed: '✓',
  running: '▶',
  failed: '✗',
  pending: '○',
}

export default function StepTabs({ activeStep, onStepChange, stepStatuses }: StepTabsProps) {
  return (
    <div className="flex gap-1 overflow-x-auto pb-2">
      {STEP_NAMES.map((step) => {
        const status = stepStatuses[step]?.status || 'pending'
        const isActive = step === activeStep
        const rating = stepStatuses[step]?.last_rating

        return (
          <button
            key={step}
            onClick={() => onStepChange(step)}
            className={`
              flex items-center gap-1.5 px-3 py-2 rounded-lg border text-sm font-medium
              whitespace-nowrap transition-all
              ${isActive ? 'ring-2 ring-indigo-500 shadow-sm' : ''}
              ${STATUS_STYLES[status]}
            `}
            title={STEP_DESCRIPTIONS[step]}
          >
            <span>{STATUS_ICONS[status]}</span>
            <span>{STEP_SHORT_NAMES[step]}</span>
            {rating && <span className="text-yellow-500 text-xs">{'★'.repeat(rating)}</span>}
          </button>
        )
      })}
    </div>
  )
}
