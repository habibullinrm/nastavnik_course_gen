'use client'

import React from 'react'

export type FieldImportance = 'critical' | 'important' | 'optional'

interface FieldWithBadgeProps {
  label: string
  importance: FieldImportance
  htmlFor?: string
  error?: string
  hint?: string
  children: React.ReactNode
}

const BADGE_CONFIG: Record<FieldImportance, { emoji: string; label: string; className: string }> = {
  critical: { emoji: '🔴', label: 'CRITICAL', className: 'bg-red-100 text-red-700 border-red-200' },
  important: { emoji: '🟡', label: 'IMPORTANT', className: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  optional: { emoji: '🟢', label: 'OPTIONAL', className: 'bg-green-100 text-green-700 border-green-200' },
}

export default function FieldWithBadge({
  label,
  importance,
  htmlFor,
  error,
  hint,
  children,
}: FieldWithBadgeProps) {
  const badge = BADGE_CONFIG[importance]

  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-1">
        <label htmlFor={htmlFor} className="text-sm font-medium text-gray-700">
          {label}
        </label>
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-medium ${badge.className}`}
          title={badge.label}
        >
          {badge.emoji} {badge.label}
        </span>
      </div>
      {hint && <p className="text-xs text-gray-500 mb-1">{hint}</p>}
      {children}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  )
}
