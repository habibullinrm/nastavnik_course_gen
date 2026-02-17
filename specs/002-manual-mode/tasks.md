# 002-manual-mode: Задачи

## Этап 1: Foundation

- [x] T01: Миграция 004 — 4 новые таблицы (manual_sessions, prompt_versions, manual_step_runs, processor_configs)
- [x] T02: SQLAlchemy модели (ManualSession, PromptVersion, ManualStepRun, ProcessorConfig)
- [x] T03: Backend Pydantic schemas (manual.py)
- [x] T04: ML manual_executor.py — выполнение шага с кастомным промптом
- [x] T05: ML schemas (manual.py) + endpoints (execute-step, render-prompt, baseline)
- [x] T06: Backend manual_service.py — CRUD сессий + оркестрация шагов
- [x] T07: Backend manual.py router — session + step + prompt endpoints

## Этап 2: Промпты

- [x] T08: ML prompt_reader.py — чтение baseline из .py файлов
- [x] T09: Backend prompt_service.py — версионирование промптов
- [x] T10: Backend prompt endpoints в router

## Этап 3: Frontend MVP

- [x] T11: TypeScript типы (manual.ts) + API клиент (manualApi.ts)
- [x] T12: Страница списка сессий + создание
- [x] T13: Рабочее пространство сессии (основная страница)
- [x] T14: Компоненты: StepTabs, PromptEditor, StepRunResult, JsonViewer, UserRating, RunHistory

## Этап 4: Процессоры и оценка

- [x] T15: ml/processors/ — структура + примеры
- [x] T16: ML endpoints: processors discovery + run
- [x] T17: Backend evaluation_service — авто-метрики
- [x] T18: Frontend: ProcessorConfig, AutoEvaluation

## Этап 5: Polish

- [x] T19: LLM-as-Judge оценка (ML evaluate endpoint)
- [x] T20: Редактор профиля (отдельная страница)
- [x] T21: Браузер версий промптов
- [x] T22: InputDataEditor (ручной ввод JSON)
