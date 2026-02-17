'use client'

import { useState } from 'react'

interface JsonViewerProps {
  data: unknown
  title?: string
  defaultExpanded?: boolean
  maxHeight?: string
}

export default function JsonViewer({ data, title, defaultExpanded = false, maxHeight = '400px' }: JsonViewerProps) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  if (data === null || data === undefined) {
    return <span className="text-gray-400 text-sm italic">null</span>
  }

  const jsonStr = typeof data === 'string' ? data : JSON.stringify(data, null, 2)

  return (
    <div className="border rounded-lg overflow-hidden">
      {title && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 bg-gray-50 text-left text-sm font-medium text-gray-700 hover:bg-gray-100 flex justify-between items-center"
        >
          <span>{title}</span>
          <span className="text-xs text-gray-400">{expanded ? '▼' : '▶'}</span>
        </button>
      )}
      {(expanded || !title) && (
        <pre
          className="p-3 text-xs bg-gray-900 text-green-400 overflow-auto"
          style={{ maxHeight }}
        >
          {jsonStr}
        </pre>
      )}
    </div>
  )
}
