'use client'

import { useState } from 'react'
import EmptySection from '@/components/Track/EmptySection'
import { LearningUnitsData, HierarchyData, LEVEL_LABELS } from '@/types/track'

interface LearningTreeProps {
  units?: LearningUnitsData
  hierarchy?: HierarchyData
}

const UNIT_TYPE_STYLES: Record<string, { label: string; badge: string }> = {
  theory: { label: 'Теория', badge: 'bg-sky-100 text-sky-700' },
  practice: { label: 'Практика', badge: 'bg-emerald-100 text-emerald-700' },
  automation: { label: 'Автоматизм', badge: 'bg-violet-100 text-violet-700' },
}

/** Дерево учебных единиц из шагов B4/B5. Уровень → Кластер → Юниты. */
export default function TreeView({ units, hierarchy }: LearningTreeProps) {
  if (!units || !hierarchy) {
    return <EmptySection message="Учебные единицы не сгенерированы" step="B4/B5" />
  }

  // Создаём словари для быстрого поиска
  const theoryMap = new Map(units.theory_units.map(u => [u.id, u]))
  const practiceMap = new Map(units.practice_units.map(u => [u.id, u]))
  const automationMap = new Map(units.automation_units.map(u => [u.id, u]))
  const clusterMap = new Map(units.clusters.map(c => [c.id, c]))

  const totalUnits =
    units.theory_units.length +
    units.practice_units.length +
    units.automation_units.length

  return (
    <div className="space-y-4">
      {/* Итоги */}
      <div className="flex items-center gap-6 text-sm text-gray-600 bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
        <span>
          <strong className="text-gray-900">{hierarchy.total_weeks}</strong> нед.
        </span>
        <span>
          <strong className="text-gray-900">{units.clusters.length}</strong> кластеров
        </span>
        <span>
          <strong className="text-gray-900">{totalUnits}</strong> юнитов
        </span>
        {hierarchy.time_compression_applied && (
          <span className="text-amber-600 text-xs font-medium">⚡ Время сжато</span>
        )}
      </div>

      {/* Дерево: Уровни → Кластеры → Юниты */}
      <div className="space-y-3">
        {hierarchy.levels.map(level => (
          <LevelNode
            key={level.level}
            level={level}
            clusterMap={clusterMap}
            theoryMap={theoryMap}
            practiceMap={practiceMap}
            automationMap={automationMap}
          />
        ))}
      </div>
    </div>
  )
}

function LevelNode({
  level,
  clusterMap,
  theoryMap,
  practiceMap,
  automationMap,
}: {
  level: HierarchyData['levels'][0]
  clusterMap: Map<string, LearningUnitsData['clusters'][0]>
  theoryMap: Map<string, LearningUnitsData['theory_units'][0]>
  practiceMap: Map<string, LearningUnitsData['practice_units'][0]>
  automationMap: Map<string, LearningUnitsData['automation_units'][0]>
}) {
  const [open, setOpen] = useState(true)

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 bg-gray-50 text-left hover:bg-gray-100 transition-colors"
      >
        <span className="text-xs font-mono bg-gray-200 text-gray-600 px-2 py-0.5 rounded">
          {LEVEL_LABELS[level.level] ?? level.level}
        </span>
        <span className="text-sm font-medium text-gray-700 flex-1">
          {level.clusters.length} кластеров · {level.estimated_weeks} нед.
        </span>
        <span className="text-gray-400 text-xs">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-4 py-3 space-y-3 bg-white">
          {level.clusters.map(clusterId => {
            const cluster = clusterMap.get(clusterId)
            if (!cluster) return null
            return (
              <ClusterNode
                key={clusterId}
                cluster={cluster}
                theoryMap={theoryMap}
                practiceMap={practiceMap}
                automationMap={automationMap}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

function ClusterNode({
  cluster,
  theoryMap,
  practiceMap,
  automationMap,
}: {
  cluster: LearningUnitsData['clusters'][0]
  theoryMap: Map<string, LearningUnitsData['theory_units'][0]>
  practiceMap: Map<string, LearningUnitsData['practice_units'][0]>
  automationMap: Map<string, LearningUnitsData['automation_units'][0]>
}) {
  const [open, setOpen] = useState(false)

  const unitCount =
    cluster.theory_units.length +
    cluster.practice_units.length +
    cluster.automation_units.length

  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-3 py-2.5 bg-gray-50 text-left hover:bg-gray-100 transition-colors"
      >
        <span className="text-xs font-mono text-gray-400">{cluster.id}</span>
        <span className="text-sm text-gray-800 flex-1 font-medium">{cluster.title}</span>
        <span className="text-xs text-gray-400 shrink-0">
          {unitCount} юн · {cluster.total_minutes} мин
        </span>
        <span className="text-gray-400 text-xs ml-1">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-3 py-2 space-y-1 bg-white">
          {cluster.theory_units.map(id => {
            const u = theoryMap.get(id)
            return u ? <UnitRow key={id} id={id} title={u.title} minutes={u.estimated_minutes} type="theory" /> : null
          })}
          {cluster.practice_units.map(id => {
            const u = practiceMap.get(id)
            return u ? <UnitRow key={id} id={id} title={u.title} minutes={u.estimated_minutes} type="practice" /> : null
          })}
          {cluster.automation_units.map(id => {
            const u = automationMap.get(id)
            return u ? <UnitRow key={id} id={id} title={u.title} minutes={u.estimated_minutes} type="automation" /> : null
          })}
        </div>
      )}
    </div>
  )
}

function UnitRow({
  id,
  title,
  minutes,
  type,
}: {
  id: string
  title: string
  minutes: number
  type: 'theory' | 'practice' | 'automation'
}) {
  const style = UNIT_TYPE_STYLES[type]
  return (
    <div className="flex items-center gap-2 py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-xs font-mono text-gray-300 w-8 shrink-0">{id}</span>
      <span className="text-sm text-gray-700 flex-1">{title}</span>
      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${style.badge}`}>
        {style.label}
      </span>
      <span className="text-xs text-gray-400 shrink-0 w-14 text-right">{minutes} мин</span>
    </div>
  )
}
