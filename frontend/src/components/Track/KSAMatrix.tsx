'use client'

import { useState } from 'react'
import EmptySection from './EmptySection'
import { KSAMatrixData } from '@/types/track'

interface KSAMatrixProps {
  data?: KSAMatrixData
}

interface KSAItemRowProps {
  id: string
  title: string
  description: string
  source: string
}

function KSAItemRow({ id, title, description, source }: KSAItemRowProps) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border-b border-gray-100 last:border-0">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-start gap-3 py-2.5 text-left hover:bg-gray-50 px-1 rounded transition-colors"
      >
        <span className="text-gray-400 text-xs font-mono mt-0.5 shrink-0 w-8">{id}</span>
        <span className="text-sm text-gray-800 flex-1">{title}</span>
        <span className="text-gray-400 text-xs mt-0.5 shrink-0">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="pb-3 pl-11 pr-1">
          <p className="text-sm text-gray-600 leading-relaxed mb-1">{description}</p>
          <p className="text-xs text-gray-400 italic">Источник: {source}</p>
        </div>
      )}
    </div>
  )
}

function KSASection({
  title,
  color,
  items,
  emptyMsg,
}: {
  title: string
  color: string
  items: KSAItemRowProps[]
  emptyMsg: string
}) {
  const [open, setOpen] = useState(true)
  return (
    <div className={`rounded-lg border ${color} overflow-hidden`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 font-medium text-sm"
      >
        <span>{title}</span>
        <span className="flex items-center gap-2">
          <span className="text-xs font-normal opacity-70">{items.length} шт.</span>
          <span>{open ? '▲' : '▼'}</span>
        </span>
      </button>
      {open && (
        <div className="px-4 pb-2 bg-white">
          {items.length === 0 ? (
            <p className="text-sm text-gray-400 py-3">{emptyMsg}</p>
          ) : (
            items.map(item => <KSAItemRow key={item.id} {...item} />)
          )}
        </div>
      )}
    </div>
  )
}

/** ЗУН-матрица из шага B3: три секции — Знания, Умения, Навыки. */
export default function KSAMatrix({ data }: KSAMatrixProps) {
  if (!data) {
    return <EmptySection message="ЗУН-матрица не сгенерирована" step="B3" />
  }

  const total =
    (data.knowledge_items?.length ?? 0) +
    (data.skill_items?.length ?? 0) +
    (data.habit_items?.length ?? 0)

  if (total === 0) {
    return <EmptySection message="ЗУН-матрица пуста" step="B3" />
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          ЗУН-матрица
        </h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
          {total} элементов
        </span>
      </div>

      <KSASection
        title="Знания (К)"
        color="border-sky-200 bg-sky-50"
        items={data.knowledge_items ?? []}
        emptyMsg="Нет элементов знаний"
      />
      <KSASection
        title="Умения (У)"
        color="border-emerald-200 bg-emerald-50"
        items={data.skill_items ?? []}
        emptyMsg="Нет элементов умений"
      />
      <KSASection
        title="Навыки (Н)"
        color="border-violet-200 bg-violet-50"
        items={data.habit_items ?? []}
        emptyMsg="Нет элементов навыков"
      />
    </div>
  )
}
