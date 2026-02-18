# Research: Manual Profile Editor (003-manual-profile)

## Контекст

Фича добавляет браузерную форму для создания и редактирования JSON-профиля студента.
Исследование охватывает: существующую инфраструктуру, структуру полей phase_a.md,
необходимые изменения в backend и frontend.

---

## 1. Существующая инфраструктура профилей

### Решение: переиспользовать существующий backend, добавить 2 эндпоинта

**Что уже есть:**

| Компонент | Путь | Описание |
|---|---|---|
| SQLAlchemy модель | `backend/src/models/student_profile.py` | Таблица `student_profiles` с JSONB `data` |
| Pydantic схема | `backend/src/schemas/student_profile.py` | `StudentProfileInput` — все поля Phase A |
| Сервис | `backend/src/services/profile_service.py` | upload_and_validate, get_profile, list_profiles |
| API роутер | `backend/src/api/profiles.py` | POST /api/profiles (file), GET /api/profiles, GET /api/profiles/{id} |
| Frontend компонент | `frontend/src/components/ProfileUpload/` | Drag-and-drop загрузка JSON-файла |
| Страница списка | `frontend/src/app/profiles/page.tsx` | Таблица всех профилей |

**Что нужно добавить:**
- `POST /api/profiles/form` — создание профиля из JSON body (не file upload)
- `PUT /api/profiles/{id}` — обновление существующего профиля
- Запись JSON-файла в `storage/profiles/{id}.json` при создании/обновлении

**Ратиональ:** существующий `StudentProfileInput` уже содержит все поля phase_a.md.
Новые эндпоинты принимают тот же Pydantic-объект, только через JSON body, не form-data.

---

## 2. Структура полей Phase A → форма

### Решение: 6 блоков = 6 секций формы, каждое поле с бейджем значимости

Полная карта полей (49 полей из phase_a.md):

| Блок | Шаг | Поле | Тип | Значимость | Тип виджета |
|---|---|---|---|---|---|
| 0 | 0.1 | `topic` | string | 🔴 CRITICAL | text input |
| 0 | 0.1 | `subject_area` | string | 🔴 CRITICAL | text input |
| 0 | 0.1 | `topic_scope` | string | 🟡 IMPORTANT | textarea |
| 1 | 1.1 | `role` | string | 🟡 IMPORTANT | text input |
| 1 | 1.1 | `experience_level` | enum | 🔴 CRITICAL | select |
| 1 | 1.1 | `formal_education` | string | 🟢 OPTIONAL | textarea |
| 1 | 1.1 | `identified_risks` | string[] | 🟡 IMPORTANT | dynamic list |
| 1 | 1.1 | `novice_mode` | bool | авто | hidden (derived) |
| 1 | 1.2 | `motivation_external` | string | 🟡 IMPORTANT | textarea |
| 1 | 1.2 | `motivation_internal` | string | 🟢 OPTIONAL | textarea |
| 1 | 1.2 | `goal_type` | enum | 🟡 IMPORTANT | select |
| 1 | 1.2 | `has_deadline` | bool | 🟡 IMPORTANT | checkbox |
| 1 | 1.2 | `deadline_date` | date | 🟡 IMPORTANT | date picker (if has_deadline) |
| 1 | 1.3 | `desired_outcomes` | string[] | 🔴 CRITICAL | dynamic list |
| 1 | 1.3 | `target_context` | string | 🟡 IMPORTANT | textarea |
| 1 | 1.3 | `outcome_source` | enum | 🟢 OPTIONAL | select |
| 2 | 2.1 | `target_tasks` | Task[] | 🔴 CRITICAL | task editor |
| 2 | 2.1 | `tasks_source` | enum | 🟢 OPTIONAL | select |
| 2 | 2.2 | `task_hierarchy` | Task[] | 🔴 CRITICAL | reorder list |
| 2 | 2.2 | `easiest_task_id` | string | 🔴 CRITICAL | select from tasks |
| 2 | 2.2 | `peak_task_id` | string | 🔴 CRITICAL | select from tasks |
| 2 | 2.3 | `subtasks` | Subtask[] | 🔴 CRITICAL | subtask editor |
| 2 | 2.3 | `subtasks_source` | enum | 🟢 OPTIONAL | select |
| 2 | 2.3 | `already_known_subtasks` | string[] | 🟡 IMPORTANT | multi-select |
| 2 | 2.4 | `primary_context` | string | 🟡 IMPORTANT | text |
| 2 | 2.4 | `secondary_context` | string | 🟢 OPTIONAL | text |
| 2 | 2.4 | `context_type` | enum | 🟡 IMPORTANT | select |
| 3 | 3.1 | `current_approach` | string | 🟡 IMPORTANT | textarea |
| 3 | 3.1 | `approach_gaps` | string[] | 🟡 IMPORTANT | dynamic list |
| 3 | 3.1 | `diagnostic_result` | enum | 🔴 CRITICAL | select |
| 3 | 3.2 | `key_barriers` | Barrier[] | 🟡 IMPORTANT | barrier editor |
| 3 | 3.2 | `barriers_source` | enum | 🟢 OPTIONAL | select |
| 3 | 3.3 | `confusing_concepts` | Concept[] | 🔴 CRITICAL | concept editor |
| 3 | 3.3 | `concepts_source` | enum | 🟢 OPTIONAL | select |
| 3 | 3.4 | `theory_format_preference` | enum | 🟡 IMPORTANT | select |
| 3 | 3.4 | `theory_format_details` | string | 🟢 OPTIONAL | textarea |
| 3 | 3.4 | `best_material_reference` | string | 🟢 OPTIONAL | text |
| 4 | 4.1 | `instruction_format` | string[] | 🟡 IMPORTANT | multi-checkbox |
| 4 | 4.2 | `feedback_type` | string[] | 🟡 IMPORTANT | multi-checkbox |
| 4 | 4.2 | `practice_format` | string[] | 🟡 IMPORTANT | multi-checkbox |
| 4 | 4.3 | `daily_practice_minutes` | int | 🟡 IMPORTANT | number |
| 4 | 4.3 | `practice_windows` | PracticeWindow[] | 🟢 OPTIONAL | schedule editor |
| 4 | 4.3 | `needs_reminder` | bool | 🟢 OPTIONAL | checkbox |
| 4 | 4.4 | `mastery_signals` | string[] | 🟢 OPTIONAL | dynamic list |
| 4 | 4.4 | `support_tools` | string[] | 🟢 OPTIONAL | multi-checkbox |
| 5 | 5.1 | `weekly_hours` | float | 🔴 CRITICAL | number |
| 5 | 5.1 | `schedule` | Schedule[] | 🟡 IMPORTANT | day editor |
| 5 | 5.2 | `learning_format` | enum | 🟡 IMPORTANT | select |
| 5 | 5.2 | `support_channel` | string | 🟢 OPTIONAL | text |
| — | — | `success_criteria` | Criterion[] | 🔴 CRITICAL | criterion editor |

---

## 3. Выгрузка профиля

### Решение: кнопка «Скачать JSON» на странице формы — браузерный download без серверного файлового хранилища

**Ратиональ:** профиль хранится в PostgreSQL. Выгрузка реализуется на frontend через
`Blob` + `URL.createObjectURL` — браузер сохраняет файл локально без дополнительного
API-запроса. Имя файла: `profile-{topic_slug}.json`.

**Альтернативы отклонены:**
- Сохранение в `storage/profiles/` на сервере — избыточно, усложняет инфраструктуру

---

## 4. Выводы

| Вопрос | Решение |
|---|---|
| Новые эндпоинты | POST /api/profiles/form + PUT /api/profiles/{id} |
| Pydantic схема | Переиспользовать `StudentProfileInput`, уже содержит все поля |
| Хранилище | PostgreSQL (единственное хранилище) |
| Выгрузка профиля | Браузерный download через Blob API, без серверного эндпоинта |
| Frontend фреймворк | Next.js 14 + App Router, Tailwind CSS (по конституции) |
| Form state | React useState + кастомный хук `useProfileForm` (без новых библиотек) |
| Валидация frontend | Inline validation по значимости (CRITICAL обязательны) |
| Роутинг | /profiles/new, /profiles/[id]/edit (новые страницы) |