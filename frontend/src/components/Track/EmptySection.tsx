'use client'

interface EmptySectionProps {
  message: string
  step?: string
  variant?: 'empty' | 'error' | 'loading'
}

/** Переиспользуемая заглушка для разделов трека при отсутствии данных. */
export default function EmptySection({ message, step, variant = 'empty' }: EmptySectionProps) {
  const styles = {
    empty: 'bg-gray-50 border-gray-200 text-gray-500',
    error: 'bg-red-50 border-red-200 text-red-600',
    loading: 'bg-blue-50 border-blue-200 text-blue-600',
  }

  const icons = {
    empty: '—',
    error: '✕',
    loading: '⋯',
  }

  return (
    <div className={`border rounded-lg p-8 text-center ${styles[variant]}`}>
      <div className="text-2xl mb-2">{icons[variant]}</div>
      <p className="text-sm font-medium">{message}</p>
      {step && (
        <p className="text-xs mt-1 opacity-70">Шаг {step}</p>
      )}
    </div>
  )
}
