'use client'

import React, { useState } from 'react'

interface ProfileSectionProps {
  title: string
  icon?: string
  defaultOpen?: boolean
  criticalTotal?: number
  criticalFilled?: number
  children: React.ReactNode
}

export default function ProfileSection({
  title,
  icon,
  defaultOpen = true,
  criticalTotal = 0,
  criticalFilled = 0,
  children,
}: ProfileSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const allFilled = criticalTotal > 0 && criticalFilled >= criticalTotal

  return (
    <div className="border border-gray-200 rounded-lg mb-4 overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon && <span className="text-lg">{icon}</span>}
          <span className="font-semibold text-gray-800">{title}</span>
          {criticalTotal > 0 && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                allFilled ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
              }`}
            >
              {criticalFilled} / {criticalTotal} CRITICAL
            </span>
          )}
        </div>
        <span className="text-gray-400 text-sm">{isOpen ? '▲' : '▼'}</span>
      </button>
      {isOpen && <div className="px-4 py-4">{children}</div>}
    </div>
  )
}
