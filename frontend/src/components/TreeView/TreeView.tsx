/**
 * Компонент древовидного отображения трека
 *
 * Рекурсивное отображение структуры:
 * Компетенции → ЗУН → Учебные единицы → Уровни → Недели → Дни
 */

'use client'

import { useState } from 'react'

interface Competency {
  id: string
  title?: string
  description?: string
}

interface KnowledgeItem {
  id: string
  title?: string
}

interface SkillItem {
  id: string
  title?: string
}

interface LearningUnit {
  id: string
  title: string
  type: string
}

interface TrackData {
  competency_set?: {
    competencies?: Competency[]
  }
  ksa_matrix?: {
    knowledge_items?: KnowledgeItem[]
    skill_items?: SkillItem[]
  }
  learning_units?: LearningUnit[]
}

interface TreeViewProps {
  trackData: TrackData | null
}

export default function TreeView({ trackData }: TreeViewProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  if (!trackData) {
    return <div className="text-gray-500">Нет данных для отображения</div>
  }

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  return (
    <div className="space-y-4">
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Структура курса</h3>

        {/* Competencies */}
        {trackData.competency_set?.competencies && (
          <div className="space-y-2">
            <button
              onClick={() => toggleNode('competencies')}
              className="flex items-center gap-2 text-left font-medium text-gray-900 hover:text-blue-600"
            >
              <span>{expandedNodes.has('competencies') ? '▼' : '▶'}</span>
              <span>Компетенции ({trackData.competency_set.competencies.length})</span>
            </button>

            {expandedNodes.has('competencies') && (
              <div className="ml-6 space-y-2">
                {trackData.competency_set.competencies.map((comp, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded border border-gray-200">
                    <div className="font-medium">{comp.title || comp.id}</div>
                    <div className="text-sm text-gray-600">{comp.description}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* KSA Matrix */}
        {trackData.ksa_matrix && (
          <div className="mt-4 space-y-2">
            <button
              onClick={() => toggleNode('ksa')}
              className="flex items-center gap-2 text-left font-medium text-gray-900 hover:text-blue-600"
            >
              <span>{expandedNodes.has('ksa') ? '▼' : '▶'}</span>
              <span>Матрица ЗУН</span>
            </button>

            {expandedNodes.has('ksa') && (
              <div className="ml-6 space-y-3">
                {trackData.ksa_matrix.knowledge_items && (
                  <div>
                    <div className="font-medium text-sm text-gray-700">
                      Знания ({trackData.ksa_matrix.knowledge_items.length})
                    </div>
                    <ul className="ml-4 mt-1 text-sm text-gray-600 list-disc">
                      {trackData.ksa_matrix.knowledge_items.slice(0, 5).map((item, idx) => (
                        <li key={idx}>{item.title || item.id}</li>
                      ))}
                      {trackData.ksa_matrix.knowledge_items.length > 5 && (
                        <li className="text-gray-400">... ещё {trackData.ksa_matrix.knowledge_items.length - 5}</li>
                      )}
                    </ul>
                  </div>
                )}

                {trackData.ksa_matrix.skill_items && (
                  <div>
                    <div className="font-medium text-sm text-gray-700">
                      Умения ({trackData.ksa_matrix.skill_items.length})
                    </div>
                    <ul className="ml-4 mt-1 text-sm text-gray-600 list-disc">
                      {trackData.ksa_matrix.skill_items.slice(0, 5).map((item, idx) => (
                        <li key={idx}>{item.title || item.id}</li>
                      ))}
                      {trackData.ksa_matrix.skill_items.length > 5 && (
                        <li className="text-gray-400">... ещё {trackData.ksa_matrix.skill_items.length - 5}</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Learning Units */}
        {trackData.learning_units && trackData.learning_units.length > 0 && (
          <div className="mt-4 space-y-2">
            <button
              onClick={() => toggleNode('units')}
              className="flex items-center gap-2 text-left font-medium text-gray-900 hover:text-blue-600"
            >
              <span>{expandedNodes.has('units') ? '▼' : '▶'}</span>
              <span>Учебные единицы ({trackData.learning_units.length})</span>
            </button>

            {expandedNodes.has('units') && (
              <div className="ml-6 space-y-2">
                {trackData.learning_units.slice(0, 10).map((unit, idx) => (
                  <div key={idx} className="p-2 bg-gray-50 rounded text-sm">
                    <span className="font-medium">{unit.title}</span>
                    <span className="text-gray-500 ml-2">({unit.type})</span>
                  </div>
                ))}
                {trackData.learning_units.length > 10 && (
                  <div className="text-sm text-gray-400">
                    ... ещё {trackData.learning_units.length - 10} единиц
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
