'use client'

import { useState, useCallback } from 'react'
import type {
  ProfileFormState,
  ProfileFormTask,
  ProfileFormSubtask,
  ProfileFormBarrier,
  ProfileFormConcept,
  ProfileFormScheduleDay,
  ProfileFormPracticeWindow,
  ProfileFormSuccessCriterion,
} from '@/types'
import { DEFAULT_PROFILE_FORM } from '@/types'

// Поля, которые блокируют отправку формы при пустых значениях
const CRITICAL_STRING_FIELDS: (keyof ProfileFormState)[] = [
  'topic',
  'subject_area',
  'experience_level',
  'diagnostic_result',
]

const CRITICAL_ARRAY_FIELDS: (keyof ProfileFormState)[] = [
  'desired_outcomes',
  'target_tasks',
  'subtasks',
  'confusing_concepts',
  'success_criteria',
]

export interface FormValidationError {
  field: string
  message: string
}

// Типы для массивных полей
type ArrayFieldItem =
  | string
  | ProfileFormTask
  | ProfileFormSubtask
  | ProfileFormBarrier
  | ProfileFormConcept
  | ProfileFormScheduleDay
  | ProfileFormPracticeWindow
  | ProfileFormSuccessCriterion

type ArrayField = keyof {
  [K in keyof ProfileFormState as ProfileFormState[K] extends Array<unknown> ? K : never]: ProfileFormState[K]
}

export function useProfileForm(initial?: Partial<ProfileFormState>) {
  const [state, setState] = useState<ProfileFormState>({
    ...DEFAULT_PROFILE_FORM,
    ...initial,
  })

  // Установить значение скалярного поля
  const setField = useCallback(<K extends keyof ProfileFormState>(
    key: K,
    value: ProfileFormState[K]
  ) => {
    setState(prev => {
      const next = { ...prev, [key]: value }
      // Автоматически обновляем novice_mode на основе experience_level
      if (key === 'experience_level') {
        const level = value as string
        next.novice_mode = level === 'zero' || level === 'beginner'
      }
      return next
    })
  }, [])

  // Добавить элемент в массивное поле
  const addItem = useCallback(<K extends ArrayField>(
    key: K,
    item: ArrayFieldItem
  ) => {
    setState(prev => ({
      ...prev,
      [key]: [...(prev[key] as ArrayFieldItem[]), item],
    }))
  }, [])

  // Удалить элемент из массивного поля по индексу
  const removeItem = useCallback(<K extends ArrayField>(
    key: K,
    index: number
  ) => {
    setState(prev => ({
      ...prev,
      [key]: (prev[key] as ArrayFieldItem[]).filter((_, i) => i !== index),
    }))
  }, [])

  // Обновить элемент массивного поля по индексу
  const updateItem = useCallback(<K extends ArrayField>(
    key: K,
    index: number,
    item: ArrayFieldItem
  ) => {
    setState(prev => {
      const arr = [...(prev[key] as ArrayFieldItem[])]
      arr[index] = item
      return { ...prev, [key]: arr }
    })
  }, [])

  // Валидация CRITICAL полей
  const validate = useCallback((): FormValidationError[] => {
    const errors: FormValidationError[] = []

    for (const field of CRITICAL_STRING_FIELDS) {
      const value = state[field]
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        errors.push({ field: field as string, message: `Поле обязательно для заполнения` })
      }
    }

    for (const field of CRITICAL_ARRAY_FIELDS) {
      const value = state[field]
      if (!Array.isArray(value) || value.length === 0) {
        errors.push({ field: field as string, message: `Необходимо добавить хотя бы один элемент` })
      }
    }

    if (state.target_tasks.length > 0) {
      if (!state.easiest_task_id) {
        errors.push({ field: 'easiest_task_id', message: 'Выберите самую простую задачу' })
      }
      if (!state.peak_task_id) {
        errors.push({ field: 'peak_task_id', message: 'Выберите вершинную задачу' })
      }
      const taskIds = new Set(state.target_tasks.map(t => t.id))
      if (state.easiest_task_id && !taskIds.has(state.easiest_task_id)) {
        errors.push({ field: 'easiest_task_id', message: 'Выбранная задача не найдена в списке' })
      }
      if (state.peak_task_id && !taskIds.has(state.peak_task_id)) {
        errors.push({ field: 'peak_task_id', message: 'Выбранная задача не найдена в списке' })
      }
    }

    if (state.weekly_hours <= 0) {
      errors.push({ field: 'weekly_hours', message: 'Количество часов должно быть больше 0' })
    }

    return errors
  }, [state])

  // Сконвертировать состояние в payload для API
  const toApiPayload = useCallback((): ProfileFormState => {
    return { ...state }
  }, [state])

  // Загрузить данные из JSON (полная перезапись)
  const loadFromJson = useCallback((data: Record<string, unknown>) => {
    setState({
      ...DEFAULT_PROFILE_FORM,
      ...data,
    } as ProfileFormState)
  }, [])

  // Сбросить форму к значениям по умолчанию
  const reset = useCallback(() => {
    setState({ ...DEFAULT_PROFILE_FORM })
  }, [])

  return {
    state,
    setField,
    addItem,
    removeItem,
    updateItem,
    validate,
    toApiPayload,
    loadFromJson,
    reset,
  }
}
