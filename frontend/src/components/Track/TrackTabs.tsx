'use client'

export type TrackTabId =
  | 'metadata'
  | 'competencies'
  | 'ksa'
  | 'tree'
  | 'blueprints'
  | 'schedule'
  | 'fields'

const TABS: { id: TrackTabId; label: string; icon: string }[] = [
  { id: 'metadata', label: 'Метаданные', icon: '📊' },
  { id: 'competencies', label: 'Компетенции', icon: '🎯' },
  { id: 'ksa', label: 'ЗУН-матрица', icon: '🧠' },
  { id: 'tree', label: 'Учебные единицы', icon: '🌳' },
  { id: 'blueprints', label: 'PBL-сценарии', icon: '📝' },
  { id: 'schedule', label: 'Расписание', icon: '📅' },
  { id: 'fields', label: 'Поля профиля', icon: '🔍' },
]

interface TrackTabsProps {
  activeTab: TrackTabId
  onTabChange: (tab: TrackTabId) => void
}

/** Горизонтальная панель вкладок страницы трека. Sticky при скролле. */
export default function TrackTabs({ activeTab, onTabChange }: TrackTabsProps) {
  return (
    <div className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
      <nav className="flex overflow-x-auto">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  )
}
