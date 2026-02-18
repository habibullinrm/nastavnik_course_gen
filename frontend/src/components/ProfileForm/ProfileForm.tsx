'use client'

import React, { useRef } from 'react'
import type { ProfileFormState } from '@/types'
import { useProfileForm, type FormValidationError } from '@/hooks/useProfileForm'
import ProfileSection from './ProfileSection'
import FieldWithBadge from './FieldWithBadge'
import DynamicList from './DynamicList'
import MultiCheckbox from './MultiCheckbox'
import ScheduleEditor from './ScheduleEditor'
import TaskEditor from './TaskEditor'
import SubtaskEditor from './SubtaskEditor'
import BarrierEditor from './BarrierEditor'
import ConceptEditor from './ConceptEditor'
import CriterionEditor from './CriterionEditor'
import ProfilePickerModal from './ProfilePickerModal'

// ─── Опции для полей с фиксированными вариантами ──────────────────────────────

const EXPERIENCE_LEVELS = [
  { value: 'zero', label: 'Нулевой (zero)' },
  { value: 'beginner', label: 'Начинающий (beginner)' },
  { value: 'intermediate', label: 'Средний (intermediate)' },
  { value: 'advanced', label: 'Продвинутый (advanced)' },
]

const DIAGNOSTIC_RESULTS = [
  { value: 'no_knowledge', label: 'Нет знаний' },
  { value: 'misconceptions', label: 'Ошибочные представления' },
  { value: 'partial', label: 'Частичные знания' },
  { value: 'solid_base', label: 'Твёрдая база' },
]

const GOAL_TYPES = [
  { value: 'applied', label: 'Прикладная' },
  { value: 'fundamental', label: 'Фундаментальная' },
  { value: 'mixed', label: 'Смешанная' },
]

const THEORY_FORMATS = [
  { value: 'visual_schemas', label: 'Визуальные схемы' },
  { value: 'examples_first', label: 'Примеры сначала' },
  { value: 'video', label: 'Видео' },
  { value: 'discussion', label: 'Обсуждение' },
  { value: 'text_formulas', label: 'Текст + формулы' },
  { value: 'mixed', label: 'Смешанный' },
]

const INSTRUCTION_FORMATS = [
  { value: 'checklist', label: 'Чеклист' },
  { value: 'worked_example', label: 'Разобранный пример' },
  { value: 'step_by_step', label: 'Пошаговая инструкция' },
  { value: 'video', label: 'Видео' },
  { value: 'text', label: 'Текст' },
]

const FEEDBACK_TYPES = [
  { value: 'error_with_explanation', label: 'Ошибка с объяснением' },
  { value: 'hint', label: 'Подсказка' },
  { value: 'correct_answer', label: 'Правильный ответ' },
  { value: 'score', label: 'Оценка' },
]

const PRACTICE_FORMATS = [
  { value: 'compare_with_standard', label: 'Сравнение с эталоном' },
  { value: 'fill_in_the_blank', label: 'Заполнить пропуски' },
  { value: 'open_ended', label: 'Открытый ответ' },
  { value: 'multiple_choice', label: 'Выбор варианта' },
  { value: 'problem_solving', label: 'Решение задач' },
]

const SUPPORT_TOOLS = [
  { value: 'progress_tracker', label: 'Трекер прогресса' },
  { value: 'flashcards', label: 'Флеш-карточки' },
  { value: 'calculator', label: 'Калькулятор' },
  { value: 'reference', label: 'Справочник' },
]

const LEARNING_FORMATS = [
  { value: 'self_paced', label: 'Самостоятельно' },
  { value: 'mentored', label: 'С ментором' },
  { value: 'group', label: 'Групповое' },
  { value: 'mixed', label: 'Смешанное' },
]

// ─── Подсчёт CRITICAL полей ───────────────────────────────────────────────────

function countBlock0(s: ProfileFormState) {
  return { total: 2, filled: [s.topic, s.subject_area].filter(Boolean).length }
}
function countBlock1(s: ProfileFormState) {
  return { total: 3, filled: [s.experience_level, s.desired_outcomes.length > 0, s.goal_type !== ''].filter(Boolean).length }
}
function countBlock2(s: ProfileFormState) {
  return {
    total: 5,
    filled: [
      s.target_tasks.length > 0,
      s.task_hierarchy.length > 0,
      s.easiest_task_id,
      s.peak_task_id,
      s.subtasks.length > 0,
    ].filter(Boolean).length,
  }
}
function countBlock3(s: ProfileFormState) {
  return {
    total: 2,
    filled: [s.diagnostic_result, s.confusing_concepts.length > 0].filter(Boolean).length,
  }
}
function countBlock5(s: ProfileFormState) {
  return { total: 2, filled: [s.weekly_hours > 0, s.success_criteria.length > 0].filter(Boolean).length }
}

// ─── Компонент ────────────────────────────────────────────────────────────────

interface ProfileFormProps {
  initialData?: Partial<ProfileFormState>
  profileId?: string
  onSave: (state: ProfileFormState) => Promise<void>
  saving?: boolean
  saveError?: string | null
  toolbarExtra?: React.ReactNode
}

export default function ProfileForm({
  initialData,
  onSave,
  saving = false,
  saveError,
  toolbarExtra,
}: ProfileFormProps) {
  const { state, setField, validate, toApiPayload, loadFromJson } = useProfileForm(initialData)
  const [errors, setErrors] = React.useState<FormValidationError[]>([])
  const [showPicker, setShowPicker] = React.useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // ── Поле ошибки для конкретного поля ───────────────────────────────────────
  const fieldError = (name: string) => errors.find(e => e.field === name)?.message

  // ── Обработчик сохранения ──────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errs = validate()
    if (errs.length > 0) {
      setErrors(errs)
      // Прокрутить к первой ошибке
      const firstField = document.querySelector('[data-error="true"]')
      firstField?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }
    setErrors([])
    await onSave(toApiPayload())
  }

  // ── Выгрузка JSON ──────────────────────────────────────────────────────────
  const handleDownload = () => {
    const slug = state.topic.toLowerCase().replace(/\s+/g, '-').slice(0, 50) || 'profile'
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `profile-${slug}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // ── Загрузка JSON ──────────────────────────────────────────────────────────
  const [loadError, setLoadError] = React.useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => {
      try {
        const data = JSON.parse(ev.target?.result as string)
        loadFromJson(data)
        setLoadError(null)
        setErrors([])
      } catch {
        setLoadError('Не удалось разобрать JSON-файл')
      }
    }
    reader.readAsText(file)
    // Сбросить input для повторной загрузки того же файла
    e.target.value = ''
  }

  const b0 = countBlock0(state)
  const b1 = countBlock1(state)
  const b2 = countBlock2(state)
  const b3 = countBlock3(state)
  const b5 = countBlock5(state)

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* ── Тулбар ─────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 mb-6 p-4 bg-white border border-gray-200 rounded-lg sticky top-0 z-10 shadow-sm">
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="sr-only"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="px-3 py-2 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
        >
          📂 Загрузить файл
        </button>
        <button
          type="button"
          onClick={handleDownload}
          className="px-3 py-2 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
        >
          💾 Выгрузить JSON
        </button>
        <button
          type="button"
          onClick={() => setShowPicker(true)}
          className="px-3 py-2 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
        >
          🗂 Выбрать из БД
        </button>
        {toolbarExtra}
        <div className="flex-1" />
        {loadError && (
          <span className="text-xs text-red-600">{loadError}</span>
        )}
        {saveError && (
          <span className="text-xs text-red-600">{saveError}</span>
        )}
        <button
          type="submit"
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {saving ? 'Сохранение...' : '✓ Сохранить профиль'}
        </button>
      </div>

      {/* ── Ошибки валидации ──────────────────────────────────────────── */}
      {errors.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-700 mb-1">Заполните обязательные поля:</p>
          <ul className="list-disc list-inside text-sm text-red-600 space-y-0.5">
            {errors.map((e, i) => <li key={i}>{e.field}: {e.message}</li>)}
          </ul>
        </div>
      )}

      {/* ── Название профиля ──────────────────────────────────────────── */}
      <div className="mb-4 p-4 bg-white border border-gray-200 rounded-lg">
        <label htmlFor="profile_name" className="block text-sm font-medium text-gray-700 mb-1">
          Название профиля <span className="text-gray-400 font-normal">(для различения в списке)</span>
        </label>
        <input
          id="profile_name"
          type="text"
          value={state.profile_name}
          onChange={e => setField('profile_name', e.target.value)}
          placeholder="Например: Вася — математическая логика — продвинутый"
          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* ── Блок 0: Тема ──────────────────────────────────────────────── */}
      <ProfileSection title="Блок 0: Тема" icon="📚" criticalTotal={b0.total} criticalFilled={b0.filled}>
        <FieldWithBadge label="Тема" importance="critical" htmlFor="topic" error={fieldError('topic')}>
          <div data-error={!!fieldError('topic')}>
            <input id="topic" type="text" value={state.topic}
              onChange={e => setField('topic', e.target.value)}
              placeholder="Элементы математической логики"
              className={`w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 ${fieldError('topic') ? 'border-red-400' : 'border-gray-300'}`}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Предметная область" importance="critical" htmlFor="subject_area" error={fieldError('subject_area')}>
          <div data-error={!!fieldError('subject_area')}>
            <input id="subject_area" type="text" value={state.subject_area}
              onChange={e => setField('subject_area', e.target.value)}
              placeholder="Математика, Информатика..."
              className={`w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 ${fieldError('subject_area') ? 'border-red-400' : 'border-gray-300'}`}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Область охвата темы" importance="important" htmlFor="topic_scope">
          <input id="topic_scope" type="text" value={state.topic_scope}
            onChange={e => setField('topic_scope', e.target.value)}
            placeholder="Краткое описание границ темы..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>
      </ProfileSection>

      {/* ── Блок 1: Контекст и мотивация ──────────────────────────────── */}
      <ProfileSection title="Блок 1: Контекст и мотивация" icon="🎯" criticalTotal={b1.total} criticalFilled={b1.filled}>
        <FieldWithBadge label="Роль / профессия" importance="important" htmlFor="role">
          <input id="role" type="text" value={state.role}
            onChange={e => setField('role', e.target.value)}
            placeholder="Студент, разработчик, аналитик..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Уровень опыта" importance="critical" error={fieldError('experience_level')}>
          <div data-error={!!fieldError('experience_level')}>
            <select value={state.experience_level}
              onChange={e => setField('experience_level', e.target.value as ProfileFormState['experience_level'])}
              className={`w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 ${fieldError('experience_level') ? 'border-red-400' : 'border-gray-300'}`}
            >
              <option value="">— выбрать уровень —</option>
              {EXPERIENCE_LEVELS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Внешняя мотивация" importance="important" htmlFor="motivation_external">
          <input id="motivation_external" type="text" value={state.motivation_external}
            onChange={e => setField('motivation_external', e.target.value)}
            placeholder="Экзамен, работа, проект..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Внутренняя мотивация" importance="optional" htmlFor="motivation_internal">
          <input id="motivation_internal" type="text" value={state.motivation_internal}
            onChange={e => setField('motivation_internal', e.target.value)}
            placeholder="Любопытство, интерес к теме..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Тип цели" importance="important">
          <select value={state.goal_type}
            onChange={e => setField('goal_type', e.target.value as ProfileFormState['goal_type'])}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">— выбрать тип —</option>
            {GOAL_TYPES.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </FieldWithBadge>

        <FieldWithBadge label="Дедлайн" importance="important">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
              <input type="checkbox" checked={state.has_deadline}
                onChange={e => setField('has_deadline', e.target.checked)}
                className="w-4 h-4"
              />
              Есть дедлайн
            </label>
            {state.has_deadline && (
              <input type="date" value={state.deadline_date}
                onChange={e => setField('deadline_date', e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            )}
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Желаемые результаты" importance="critical" error={fieldError('desired_outcomes')}>
          <div data-error={!!fieldError('desired_outcomes')}>
            <DynamicList items={state.desired_outcomes}
              onChange={items => setField('desired_outcomes', items)}
              placeholder="Строить таблицы истинности..."
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Контекст применения" importance="important" htmlFor="target_context">
          <input id="target_context" type="text" value={state.target_context}
            onChange={e => setField('target_context', e.target.value)}
            placeholder="Учёба в вузе, работа по специальности..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Выявленные риски" importance="important">
          <DynamicList items={state.identified_risks}
            onChange={items => setField('identified_risks', items)}
            placeholder="Мало времени, нет базы по математике..."
          />
        </FieldWithBadge>
      </ProfileSection>

      {/* ── Блок 2: Учебные задачи ────────────────────────────────────── */}
      <ProfileSection title="Блок 2: Учебные задачи" icon="✅" criticalTotal={b2.total} criticalFilled={b2.filled}>
        <FieldWithBadge label="Целевые задачи" importance="critical" error={fieldError('target_tasks')}>
          <div data-error={!!fieldError('target_tasks')}>
            <TaskEditor
              tasks={state.target_tasks}
              taskHierarchy={state.task_hierarchy}
              easiestTaskId={state.easiest_task_id}
              peakTaskId={state.peak_task_id}
              onTasksChange={tasks => setField('target_tasks', tasks)}
              onHierarchyChange={h => setField('task_hierarchy', h)}
              onEasiestChange={id => setField('easiest_task_id', id)}
              onPeakChange={id => setField('peak_task_id', id)}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Подзадачи" importance="critical" error={fieldError('subtasks')}>
          <div data-error={!!fieldError('subtasks')}>
            <SubtaskEditor
              subtasks={state.subtasks}
              tasks={state.target_tasks}
              onChange={subtasks => setField('subtasks', subtasks)}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Первичный контекст" importance="important" htmlFor="primary_context">
          <input id="primary_context" type="text" value={state.primary_context}
            onChange={e => setField('primary_context', e.target.value)}
            placeholder="Основной контекст использования знаний..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Известные подзадачи (уже освоены)" importance="important">
          <DynamicList items={state.already_known_subtasks}
            onChange={items => setField('already_known_subtasks', items)}
            placeholder="Подзадача, которую уже знаю..."
          />
        </FieldWithBadge>
      </ProfileSection>

      {/* ── Блок 3: Диагностика ───────────────────────────────────────── */}
      <ProfileSection title="Блок 3: Диагностика и барьеры" icon="🔍" criticalTotal={b3.total} criticalFilled={b3.filled}>
        <FieldWithBadge label="Результат диагностики" importance="critical" error={fieldError('diagnostic_result')}>
          <div data-error={!!fieldError('diagnostic_result')}>
            <select value={state.diagnostic_result}
              onChange={e => setField('diagnostic_result', e.target.value as ProfileFormState['diagnostic_result'])}
              className={`w-full px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 ${fieldError('diagnostic_result') ? 'border-red-400' : 'border-gray-300'}`}
            >
              <option value="">— выбрать результат —</option>
              {DIAGNOSTIC_RESULTS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Текущий подход к обучению" importance="important" htmlFor="current_approach">
          <textarea id="current_approach" value={state.current_approach}
            onChange={e => setField('current_approach', e.target.value)}
            placeholder="Как студент сейчас пытается учиться..."
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Пробелы в подходе" importance="important">
          <DynamicList items={state.approach_gaps}
            onChange={items => setField('approach_gaps', items)}
            placeholder="Не практикуется, нет систематики..."
          />
        </FieldWithBadge>

        <FieldWithBadge label="Ключевые барьеры" importance="important">
          <BarrierEditor
            barriers={state.key_barriers}
            tasks={state.target_tasks}
            onChange={barriers => setField('key_barriers', barriers)}
          />
        </FieldWithBadge>

        <FieldWithBadge label="Затрудняющие понятия" importance="critical" error={fieldError('confusing_concepts')}>
          <div data-error={!!fieldError('confusing_concepts')}>
            <ConceptEditor
              concepts={state.confusing_concepts}
              onChange={concepts => setField('confusing_concepts', concepts)}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Предпочтение формата теории" importance="important">
          <select value={state.theory_format_preference}
            onChange={e => setField('theory_format_preference', e.target.value as ProfileFormState['theory_format_preference'])}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">— выбрать —</option>
            {THEORY_FORMATS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
        </FieldWithBadge>
      </ProfileSection>

      {/* ── Блок 4: Практика ──────────────────────────────────────────── */}
      <ProfileSection title="Блок 4: Практика и форматы" icon="💪" defaultOpen={false}>
        <FieldWithBadge label="Форматы подачи" importance="important">
          <MultiCheckbox options={INSTRUCTION_FORMATS} selected={state.instruction_format}
            onChange={v => setField('instruction_format', v)} />
        </FieldWithBadge>

        <FieldWithBadge label="Тип обратной связи" importance="important">
          <MultiCheckbox options={FEEDBACK_TYPES} selected={state.feedback_type}
            onChange={v => setField('feedback_type', v)} />
        </FieldWithBadge>

        <FieldWithBadge label="Формат практики" importance="important">
          <MultiCheckbox options={PRACTICE_FORMATS} selected={state.practice_format}
            onChange={v => setField('practice_format', v)} />
        </FieldWithBadge>

        <FieldWithBadge label="Минут практики в день" importance="important" htmlFor="daily_practice_minutes">
          <input id="daily_practice_minutes" type="number" min={5} max={300} step={5}
            value={state.daily_practice_minutes}
            onChange={e => setField('daily_practice_minutes', parseInt(e.target.value, 10) || 10)}
            className="w-32 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </FieldWithBadge>

        <FieldWithBadge label="Инструменты поддержки" importance="optional">
          <MultiCheckbox options={SUPPORT_TOOLS} selected={state.support_tools}
            onChange={v => setField('support_tools', v)} />
        </FieldWithBadge>

        <FieldWithBadge label="Сигналы мастерства" importance="optional">
          <DynamicList items={state.mastery_signals}
            onChange={items => setField('mastery_signals', items)}
            placeholder="Могу решить задачу без подсказок..."
          />
        </FieldWithBadge>
      </ProfileSection>

      {/* ── Блок 5: Организация ───────────────────────────────────────── */}
      <ProfileSection title="Блок 5: Организация обучения" icon="🗓" criticalTotal={b5.total} criticalFilled={b5.filled} defaultOpen={false}>
        <FieldWithBadge label="Часов в неделю" importance="critical" htmlFor="weekly_hours" error={fieldError('weekly_hours')}>
          <div data-error={!!fieldError('weekly_hours')}>
            <input id="weekly_hours" type="number" min={1} max={168}
              value={state.weekly_hours}
              onChange={e => setField('weekly_hours', parseInt(e.target.value, 10) || 0)}
              className={`w-32 px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 ${fieldError('weekly_hours') ? 'border-red-400' : 'border-gray-300'}`}
            />
          </div>
        </FieldWithBadge>

        <FieldWithBadge label="Расписание по дням" importance="important">
          <ScheduleEditor schedule={state.schedule} onChange={s => setField('schedule', s)} />
        </FieldWithBadge>

        <FieldWithBadge label="Формат обучения" importance="important">
          <select value={state.learning_format}
            onChange={e => setField('learning_format', e.target.value as ProfileFormState['learning_format'])}
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">— выбрать —</option>
            {LEARNING_FORMATS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
        </FieldWithBadge>

        <FieldWithBadge label="Критерии успеха" importance="critical" error={fieldError('success_criteria')}>
          <div data-error={!!fieldError('success_criteria')}>
            <CriterionEditor
              criteria={state.success_criteria}
              onChange={criteria => setField('success_criteria', criteria)}
            />
          </div>
        </FieldWithBadge>
      </ProfileSection>

      {showPicker && (
        <ProfilePickerModal
          onSelect={(data) => {
            loadFromJson(data)
            setErrors([])
          }}
          onClose={() => setShowPicker(false)}
        />
      )}
    </form>
  )
}
