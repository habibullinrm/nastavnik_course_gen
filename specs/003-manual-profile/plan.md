# Implementation Plan: Manual Profile Editor

**Branch**: `003-manual-profile` | **Date**: 2026-02-18 | **Spec**: `specs/003-manual-profile/spec.md`

## Summary

Браузерная форма для ручного создания и редактирования JSON-профиля студента (Phase A).
Форма отражает все 49 полей из `docs/phase_a.md` с визуальными бейджами значимости
(🔴/🟡/🟢). Профиль сохраняется в PostgreSQL; пользователь может скачать JSON
кнопкой «Выгрузить», загрузить существующий файл для редактирования или выбрать
профиль из базы.

---

## Technical Context

**Language/Version**: TypeScript (Next.js 14), Python 3.11
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Tailwind CSS
**Storage**: PostgreSQL (JSONB), без файлового хранилища
**Testing**: pytest (backend), нет frontend unit-тестов (по сложившейся практике)
**Target Platform**: Web (Docker, Next.js frontend + FastAPI backend)
**Performance Goals**: форма < 200ms отклик при переключении секций (клиентская логика)
**Constraints**: только существующий стек, без новых npm/pip зависимостей
**Scale/Scope**: ~49 полей, 6 блоков, 1 форма создания + 1 форма редактирования

---

## Constitution Check

| Принцип | Статус | Комментарий |
|---|---|---|
| I. Container Isolation | ✅ | Новые страницы — в `frontend`, новые эндпоинты — в `backend`. Никаких новых контейнеров. |
| II. Technology Stack | ✅ | Next.js + Tailwind (frontend), FastAPI + SQLAlchemy (backend). Новых runtime-зависимостей нет. |
| III. Async-First | ✅ | Новые эндпоинты — `async def`. Frontend-вызовы — через существующий `api.ts`. |
| IV. Russian Documentation | ✅ | Docstrings на русском (Google format), комментарии в tsx на русском. |
| V. DeepSeek as LLM | ✅ (N/A) | Фича не использует LLM. |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Next.js)                                             │
│                                                                 │
│  /profiles/new              /profiles/[id]/edit                 │
│       │                              │                          │
│       └──────────┬───────────────────┘                          │
│                  ▼                                              │
│          <ProfileForm>                                          │
│          ├── useProfileForm (hook: state + validation)          │
│          ├── <ProfileSection> × 6  (Блок 0–5, collapsible)     │
│          │   └── <FieldWithBadge> × N  (🔴/🟡/🟢 badge)        │
│          ├── <DynamicList>  (identified_risks, desired_outcomes …)│
│          ├── <TaskEditor>   (target_tasks + task_hierarchy)     │
│          ├── <SubtaskEditor>                                    │
│          ├── <BarrierEditor>                                    │
│          ├── <ConceptEditor>                                    │
│          ├── <ScheduleEditor>  (7 дней × минуты)               │
│          ├── <MultiCheckbox>   (instruction_format, feedback…)  │
│          └── Toolbar:                                           │
│              [Выбрать из БД] [Загрузить файл] [Выгрузить JSON] │
│              [Сохранить (POST/PUT)]                             │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP (JSON body)
┌──────────────────────▼──────────────────────────────────────────┐
│  Backend (FastAPI)                                              │
│                                                                 │
│  POST /api/profiles/form  →  profile_service.create_from_form() │
│  PUT  /api/profiles/{id}  →  profile_service.update_profile()   │
│  GET  /api/profiles       →  (существующий) список для выбора   │
│  GET  /api/profiles/{id}  →  (существующий) загрузка для edit   │
│                                          │                      │
│                                          ▼                      │
│                                    PostgreSQL                   │
│                                    student_profiles             │
└─────────────────────────────────────────────────────────────────┘
```

### Ключевые решения

| Аспект | Решение | Обоснование |
|---|---|---|
| Form state | `useState` + `useProfileForm` hook | Нет сложных подписок; избегаем новых библиотек (Zustand, React Hook Form) |
| Секции формы | Collapsible блоки (Блок 0–5) | Форма из 49 полей необходима к структурированию |
| Зависимые поля | Условный рендер в JSX | `has_deadline → deadline_date`, `experience_level → novice_mode` |
| Выбор профиля из БД | Модальное окно со списком `GET /api/profiles` | Требование spec п.6 |
| Выгрузка | Браузерный `Blob` download | Без дополнительного API; мгновенно |
| Загрузка файла | Существующий `POST /api/profiles` + парсинг для формы | Повторное использование валидации |
| Новые backend-эндпоинты | `POST /form` + `PUT /{id}` | Раздельная логика создания и обновления |

---

## Project Structure

### Документация (эта фича)

```text
specs/003-manual-profile/
├── spec.md
├── plan.md          ← этот файл
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── tasks.md         ← /speckit.tasks
```

### Изменения в исходном коде

```text
backend/
└── src/
    ├── api/
    │   └── profiles.py          ИЗМЕНИТЬ: + POST /form, + PUT /{id}
    ├── services/
    │   └── profile_service.py   ИЗМЕНИТЬ: + create_from_form(), update_profile()
    └── schemas/
        └── student_profile.py   ИЗМЕНИТЬ: + ProfileFormResponse (201/200)

frontend/
└── src/
    ├── app/
    │   └── profiles/
    │       ├── new/
    │       │   └── page.tsx     СОЗДАТЬ
    │       └── [id]/
    │           └── edit/
    │               └── page.tsx СОЗДАТЬ
    ├── components/
    │   └── ProfileForm/
    │       ├── ProfileForm.tsx        СОЗДАТЬ  (главный компонент)
    │       ├── ProfileSection.tsx     СОЗДАТЬ  (collapsible блок)
    │       ├── FieldWithBadge.tsx     СОЗДАТЬ  (обёртка с бейджем 🔴/🟡/🟢)
    │       ├── DynamicList.tsx        СОЗДАТЬ  (редактируемый список строк)
    │       ├── TaskEditor.tsx         СОЗДАТЬ  (Task[] + иерархия)
    │       ├── SubtaskEditor.tsx      СОЗДАТЬ  (Subtask[])
    │       ├── BarrierEditor.tsx      СОЗДАТЬ  (Barrier[])
    │       ├── ConceptEditor.tsx      СОЗДАТЬ  (Concept[])
    │       ├── ScheduleEditor.tsx     СОЗДАТЬ  (7 дней × минуты)
    │       ├── MultiCheckbox.tsx      СОЗДАТЬ  (string[] из фиксированных вариантов)
    │       ├── ProfilePickerModal.tsx СОЗДАТЬ  (выбор профиля из БД)
    │       └── index.ts              СОЗДАТЬ  (barrel export)
    ├── hooks/
    │   └── useProfileForm.ts    СОЗДАТЬ  (state, validation, helpers)
    ├── services/
    │   └── api.ts               ИЗМЕНИТЬ: + createProfileFromForm(), updateProfile()
    └── types/
        └── index.ts             ИЗМЕНИТЬ: + ProfileFormState, Task, Subtask, ...
```

---

## Complexity Tracking

Нарушений конституции нет. Таблица не заполняется.

---

## Фазы реализации

### Фаза 1 — Backend (основа)

**Цель:** новые эндпоинты работают, Pydantic-валидация проходит.

1. Добавить `create_from_form()` и `update_profile()` в `profile_service.py`
2. Добавить `POST /api/profiles/form` и `PUT /api/profiles/{id}` в `profiles.py`
3. Добавить `ProfileFormResponse` в `schemas/student_profile.py`
4. Написать pytest-тесты для новых сервисных функций

### Фаза 2 — Frontend: типы и хук

**Цель:** данные формы корректно моделируются и валидируются на клиенте.

1. Обновить `types/index.ts`: добавить `ProfileFormState`, `Task`, `Subtask`, `Barrier`, `Concept`, `ScheduleDay`, `PracticeWindow`, `SuccessCriterion`
2. Добавить `createProfileFromForm()` и `updateProfile()` в `api.ts`
3. Создать `useProfileForm.ts`: state, setField(), addItem(), removeItem(), validate(), toApiPayload()

### Фаза 3 — Frontend: базовые UI-компоненты

**Цель:** все виджеты формы готовы изолированно.

1. `FieldWithBadge.tsx` — обёртка с бейджем значимости
2. `ProfileSection.tsx` — collapsible секция с прогресс-индикатором заполненности
3. `DynamicList.tsx` — редактируемый список строк (add/remove)
4. `MultiCheckbox.tsx` — множественный выбор из фиксированных опций
5. `ScheduleEditor.tsx` — редактор расписания по дням недели
6. `TaskEditor.tsx` — редактор Task[] + ранжирование + выбор easiest/peak
7. `SubtaskEditor.tsx`, `BarrierEditor.tsx`, `ConceptEditor.tsx`
8. `ProfilePickerModal.tsx` — модальное окно выбора профиля из БД

### Фаза 4 — Frontend: сборка формы и страницы

**Цель:** полноценные страницы создания и редактирования работают end-to-end.

1. `ProfileForm.tsx` — главный компонент, объединяет все секции и тулбар
2. `/profiles/new/page.tsx` — страница создания (пустая форма + выбор из БД + загрузка файла)
3. `/profiles/[id]/edit/page.tsx` — страница редактирования (предзагрузка из `GET /api/profiles/{id}`)
4. Кнопка «Выгрузить JSON» — браузерный download через Blob
5. Кнопка «Загрузить файл» — парсинг JSON → заполнение формы + валидация

### Фаза 5 — Интеграция и навигация

**Цель:** все страницы связаны между собой.

1. Добавить кнопки «Создать профиль» и «Редактировать» на страницу `/profiles`
2. После успешного сохранения: редирект на `/profiles/{id}/edit` или `/profiles`
3. Добавить ссылку «Профили → Создать» в навигацию