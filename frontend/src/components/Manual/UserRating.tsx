'use client'

import { useState } from 'react'

interface UserRatingProps {
  rating: number | null
  notes: string | null
  onSave: (rating: number | null, notes: string | null) => void
  disabled?: boolean
}

export default function UserRating({ rating, notes, onSave, disabled }: UserRatingProps) {
  const [currentRating, setCurrentRating] = useState(rating)
  const [currentNotes, setCurrentNotes] = useState(notes || '')
  const [hover, setHover] = useState(0)

  const handleSave = () => {
    onSave(currentRating, currentNotes || null)
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1">
        <span className="text-sm text-gray-600 mr-2">Рейтинг:</span>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            disabled={disabled}
            onClick={() => setCurrentRating(star === currentRating ? null : star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            className={`text-xl ${
              star <= (hover || currentRating || 0)
                ? 'text-yellow-400'
                : 'text-gray-300'
            } hover:scale-110 transition-transform disabled:cursor-default`}
          >
            ★
          </button>
        ))}
        {currentRating && (
          <span className="text-sm text-gray-500 ml-2">{currentRating}/5</span>
        )}
      </div>
      <textarea
        value={currentNotes}
        onChange={(e) => setCurrentNotes(e.target.value)}
        placeholder="Заметки..."
        disabled={disabled}
        className="w-full px-3 py-2 border rounded text-sm resize-none"
        rows={2}
      />
      {(currentRating !== rating || currentNotes !== (notes || '')) && (
        <button
          onClick={handleSave}
          className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
        >
          Сохранить
        </button>
      )}
    </div>
  )
}
