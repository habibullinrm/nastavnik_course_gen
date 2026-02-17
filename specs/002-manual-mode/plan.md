# 002-manual-mode: План реализации ручного режима отладки

## Обзор

Ручной режим для пошаговой отладки промптов и pipeline B1-B8:
- Запуск каждого шага по отдельности
- Версионирование промптов с откатом
- Пре/пост-процессоры (Python-файлы)
- Оценка качества (авто-метрики + LLM-as-Judge + ручная)
- Полная история запусков (snapshots)

## Архитектура

### Новые сущности

**ManualSession** — сессия отладки с копией профиля
**PromptVersion** — версии промптов для каждого шага B1-B8
**ManualStepRun** — полный снимок запуска шага (промпт + вход + ответ + оценка)
**ProcessorConfig** — привязка процессоров к шагам в сессии

### Data Flow: запуск шага

```
Frontend → POST /api/manual/sessions/{id}/steps/{step}/run
Backend manual_service.py:
  1. Загрузить сессию + profile_snapshot
  2. Вычислить input_data из предыдущего шага
  3. Загрузить prompt_version.prompt_text
  4. Запустить пре-процессоры → ML POST /manual/processors/run
  5. Вызвать ML POST /manual/execute-step
ML manual_executor.py:
  1. Получить LLM client (DeepSeek/Mock)
  2. chat_completion(prompt, schema, temp, max_tokens)
  3. Вернуть {raw_response, parsed_result, tokens, duration}
Backend (продолжение):
  6. Запустить пост-процессоры
  7. Вычислить авто-метрики
  8. Сохранить полный снимок
  9. Вернуть результат
```

### Зависимости между шагами (auto-input)

```
B1 ← profile_snapshot
B2 ← B1.parsed_result
B3 ← profile + B2.parsed_result
B4 ← B3.parsed_result
B5 ← B4.parsed_result + B1
B6 ← B4.parsed_result
B7 ← B5 + B6 + profile + B5.total_weeks
B8 ← все B1-B7 + profile
```

## Этапы реализации

### Этап 1: Foundation (Backend + ML ядро)
- Миграция 004 — 4 новые таблицы
- SQLAlchemy модели
- Backend Pydantic schemas
- ML manual_executor.py
- ML endpoints: execute-step, render-prompt
- Backend manual_service.py — CRUD + оркестрация
- Backend manual.py router

### Этап 2: Промпты
- ML prompt_reader.py — чтение baseline из .py
- Backend prompt_service.py — версионирование
- Backend prompt endpoints

### Этап 3: Frontend MVP
- TypeScript типы
- API клиент
- Страницы: список сессий, рабочее пространство
- Компоненты: StepTabs, PromptEditor, StepRunResult, JsonViewer, UserRating, RunHistory

### Этап 4: Процессоры и оценка
- ml/processors/ — структура + примеры
- ML endpoints: processors discovery + run
- Backend evaluation_service
- Frontend: ProcessorConfig, AutoEvaluation

### Этап 5: Polish
- LLM-as-Judge
- Редактор профиля
- Браузер версий промптов
- InputDataEditor
