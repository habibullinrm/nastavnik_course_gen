# Data Model: Сервис тестирования алгоритма генерации учебных треков

**Feature**: 001-algo-testing-mvp | **Date**: 2026-02-12

## Обзор

Четыре основные сущности с реляционными связями. Вложенные структуры `PersonalizedTrack` и `StudentProfile` хранятся в JSONB-колонках PostgreSQL без нормализации.

## ER-диаграмма

```
┌─────────────────────┐       ┌──────────────────────────┐       ┌─────────────────────┐
│   student_profiles   │       │   personalized_tracks     │       │     qa_reports       │
├─────────────────────┤       ├──────────────────────────┤       ├─────────────────────┤
│ id (UUID, PK)       │──1:N─→│ id (UUID, PK)            │       │ id (UUID, PK)       │
│ data (JSONB)        │       │ profile_id (UUID, FK)    │←──N:1─│ profile_id (UUID,FK)│
│ filename (VARCHAR)  │       │ track_data (JSONB)       │       │ report_data (JSONB) │
│ validation_result   │       │ generation_metadata      │       │ batch_size (INT)    │
│   (JSONB)           │       │   (JSONB)                │       │ completed_count     │
│ created_at (TSTZ)   │       │ algorithm_version (VARCHAR)│      │   (INT)             │
│ updated_at (TSTZ)   │       │ validation_b8 (JSONB)    │       │ mean_cdv (FLOAT)    │
└─────────────────────┘       │ status (VARCHAR)         │       │ status (VARCHAR)    │
                              │ created_at (TSTZ)        │       │ created_at (TSTZ)   │
                              │ generation_duration_sec  │       │ updated_at (TSTZ)   │
                              │   (FLOAT)                │       └─────────────────────┘
                              │ updated_at (TSTZ)        │               │
                              └──────────────────────────┘               │
                                          │                              │
                                          │                              │
                                          └──────────N:1─────────────────┘
                                        (qa_report_id, nullable FK)
                                          │
                                          │
                                          ↓ 1:N
                              ┌──────────────────────────┐
                              │    generation_logs       │
                              ├──────────────────────────┤
                              │ id (UUID, PK)            │
                              │ track_id (UUID, FK)      │
                              │ step_name (VARCHAR)      │
                              │ step_output (JSONB)      │
                              │ llm_calls (JSONB[])      │
                              │ step_duration_sec (FLOAT)│
                              │ error_message (TEXT)     │
                              │ created_at (TSTZ)        │
                              └──────────────────────────┘
```

## Таблицы

### student_profiles

Загруженные JSON-профили учащихся (результат Фазы A).

| Колонка | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| `id` | UUID | NOT NULL | PK, gen_random_uuid() |
| `data` | JSONB | NOT NULL | Полная структура `StudentProfile` из phase_a.md |
| `filename` | VARCHAR(255) | NOT NULL | Имя загруженного файла |
| `validation_result` | JSONB | NOT NULL | `{ valid: bool, errors: [...], warnings: [...] }` |
| `topic` | VARCHAR(500) | NOT NULL | Извлечённая тема (для отображения в списках) |
| `experience_level` | VARCHAR(50) | NULL | Извлечённый уровень |
| `created_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now(), обновляется триггером |

**Индексы:**
- PK: `id`
- GIN: `data` (для запросов по вложенным полям)
- BTREE: `created_at DESC` (для сортировки)

**Валидация на уровне приложения (Pydantic):**
- CRITICAL-поля (`topic`, `subject_area`, `experience_level`, `desired_outcomes`, `target_tasks`, `subtasks`, `confusing_concepts`, `diagnostic_result`, `weekly_hours`, `success_criteria`) — обязательны. Ошибка при отсутствии.
- IMPORTANT-поля — опциональны, предупреждение при отсутствии.
- OPTIONAL-поля — опциональны, без предупреждений.

---

### personalized_tracks

Результаты генерации pipeline B1-B8.

| Колонка | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| `id` | UUID | NOT NULL | PK, gen_random_uuid() |
| `profile_id` | UUID | NOT NULL | FK → student_profiles.id |
| `qa_report_id` | UUID | NULL | FK → qa_reports.id (если создан в рамках batch) |
| `track_data` | JSONB | NOT NULL | Полная структура `PersonalizedTrack` |
| `generation_metadata` | JSONB | NOT NULL | `{ algorithm_version, started_at, finished_at, steps_log: [...], llm_calls_count, total_tokens }` |
| `algorithm_version` | VARCHAR(50) | NOT NULL | Семантическая версия алгоритма |
| `validation_b8` | JSONB | NULL | Результат валидации шага B8: `ValidationResult` |
| `status` | VARCHAR(20) | NOT NULL | `pending` / `generating` / `completed` / `failed` |
| `error_message` | TEXT | NULL | Сообщение ошибки (если status=failed) |
| `generation_duration_sec` | FLOAT | NULL | Длительность генерации в секундах |
| `batch_index` | INT | NULL | Номер в пакетной генерации (0-based, NULL для одиночной) |
| `created_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |

**Индексы:**
- PK: `id`
- BTREE: `profile_id` (FK lookup)
- BTREE: `qa_report_id` (FK lookup)
- BTREE: `status` (фильтрация)
- BTREE: `created_at DESC` (сортировка)

**Статусы (State transitions):**
```
pending → generating → completed
                    ↘ failed
```

---

### qa_reports

Отчёты контроля качества (пакетная генерация).

| Колонка | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| `id` | UUID | NOT NULL | PK, gen_random_uuid() |
| `profile_id` | UUID | NOT NULL | FK → student_profiles.id |
| `report_data` | JSONB | NULL | Полная структура `QAReport` (заполняется после завершения) |
| `batch_size` | INT | NOT NULL | Запрошенное количество генераций (1–100) |
| `completed_count` | INT | NOT NULL | Количество успешно завершённых генераций (DEFAULT 0) |
| `mean_cdv` | FLOAT | NULL | Средний CDV между всеми парами (заполняется после расчёта) |
| `cdv_std` | FLOAT | NULL | Стандартное отклонение CDV |
| `recommendation` | VARCHAR(50) | NULL | `stable` / `needs_improvement` / `unstable` |
| `status` | VARCHAR(20) | NOT NULL | `pending` / `generating` / `calculating` / `completed` / `failed` |
| `error_message` | TEXT | NULL | Сообщение ошибки |
| `created_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |

**Индексы:**
- PK: `id`
- BTREE: `profile_id` (FK lookup)
- BTREE: `status` (фильтрация)

**Статусы (State transitions):**
```
pending → generating → calculating → completed
                    ↘ failed      ↗ (partial, если не все генерации успешны)
```

---

## JSONB-структуры

### StudentProfile (data в student_profiles)

Полная структура согласно `docs/phase_a.md`. Ключевые вложенные типы:

```
StudentProfile
├── topic: string
├── subject_area: string
├── experience_level: "zero" | "beginner" | "intermediate" | "advanced"
├── desired_outcomes: string[]
├── target_tasks: Task[]
│   └── { id, description, complexity_rank }
├── task_hierarchy: Task[]
├── peak_task_id: string
├── subtasks: Subtask[]
│   └── { id, description, parent_task_id, required_knowledge[], required_skills[] }
├── key_barriers: Barrier[]
│   └── { id, description, related_task_id, barrier_type }
├── confusing_concepts: Concept[]
│   └── { id, term, confusion_description }
├── success_criteria: Criterion[]
│   └── { id, description, measurable, metric }
├── schedule: Schedule[]
│   └── { day_of_week, available_minutes }
├── practice_windows: PracticeWindow[]
│   └── { time_of_day, duration_minutes, device }
└── ... (все остальные поля из phase_a.md)
```

### PersonalizedTrack (track_data в personalized_tracks)

Полная структура согласно `docs/phase_b.md`:

```
PersonalizedTrack
├── validated_profile: ValidatedStudentProfile     # B1
├── competency_set: CompetencySet                  # B2
│   ├── competencies: Competency[]
│   ├── integral_competency_id: string
│   ├── competency_task_map: Record<string, string[]>
│   └── competency_outcome_map: Record<string, number[]>
├── ksa_matrix: KSAMatrix                          # B3
│   ├── knowledge_items: KnowledgeItem[]
│   ├── skill_items: SkillItem[]
│   ├── habit_items: HabitItem[]
│   └── dependency_graph: DependencyEdge[]
├── learning_units: LearningUnit[]                 # B4
├── unit_clusters: LearningUnitCluster[]           # B4
├── levels: TrackLevel[]                           # B5
├── unit_sequence: LearningUnit[]                  # B5
├── lesson_blueprints: LessonBlueprint[]           # B6
├── weeks: TrackWeek[]                             # B7
│   └── { week_number, level, theme, weekly_goals, days: TrackDay[], checkpoint }
├── total_weeks: number                            # B7
├── checkpoints: Checkpoint[]                      # B7
├── final_assessment: FinalAssessment              # B7
├── support_plan: SupportPlan                      # B7
├── progress_milestones: Milestone[]               # B7
└── validation: ValidationResult                   # B8
```

### QAReport (report_data в qa_reports)

```
QAReport
├── cdv_matrix: CDVPair[]
│   └── { version_a_id, version_b_id, cdv_total, cdv_topics, cdv_subtopics, cdv_activities }
├── topic_frequency: TopicFrequency[]
│   └── { topic_name, count, total_versions, frequency_pct }
├── top_stable_topics: string[]        # Топ-5 стабильных
├── top_unstable_topics: string[]      # Топ-5 нестабильных
├── mean_cdv: number
├── cdv_std: number
├── recommendation: "stable" | "needs_improvement" | "unstable"
│   # stable: CDV < 15%, needs_improvement: 15-30%, unstable: > 30%
└── generated_at: string               # ISO timestamp
```

---

### 4. generation_logs

Логи отладки pipeline — сохранение промежуточных результатов каждого шага B1-B8 для отладки алгоритма.

| Колонка | Тип | Nullable | Описание |
|---------|-----|----------|----------|
| `id` | UUID | NOT NULL | PK, gen_random_uuid() |
| `track_id` | UUID | NOT NULL | FK → personalized_tracks.id |
| `step_name` | VARCHAR(50) | NOT NULL | Название шага: "B1_validate", "B2_competencies", ..., "B8_validation" |
| `step_output` | JSONB | NOT NULL | Промежуточный результат (ValidatedStudentProfile, CompetencySet, KSAMatrix, и т.д.) |
| `llm_calls` | JSONB[] | NOT NULL | Массив LLM-вызовов: [{prompt, response, tokens, duration_ms}] |
| `step_duration_sec` | FLOAT | NOT NULL | Длительность выполнения шага |
| `error_message` | TEXT | NULL | Сообщение об ошибке (если шаг упал) |
| `created_at` | TIMESTAMPTZ | NOT NULL | DEFAULT now() |

**Индексы:**
- PK: `id`
- BTREE: `(track_id, step_name)` — быстрый поиск логов для трека
- GIN: `step_output` — JSON-запросы по содержимому

**Статусы (шаги pipeline):**
- B1_validate — валидация и обогащение профиля
- B2_competencies — формулирование компетенций
- B3_ksa_matrix — декомпозиция в матрицу ЗУН
- B4_learning_units — проектирование учебных единиц
- B5_hierarchy — иерархия и уровни
- B6_problem_formulations — проблемные формулировки
- B7_schedule — сборка расписания
- B8_validation — валидация трека

---

## Связи между сущностями

| Связь | Кардинальность | FK | Описание |
|-------|----------------|-----|----------|
| student_profiles → personalized_tracks | 1:N | personalized_tracks.profile_id | Один профиль → множество генераций |
| student_profiles → qa_reports | 1:N | qa_reports.profile_id | Один профиль → множество QA-запусков |
| qa_reports → personalized_tracks | 1:N | personalized_tracks.qa_report_id | Один QA-отчёт → N треков (batch) |
| personalized_tracks → generation_logs | 1:N | generation_logs.track_id | Один трек → 8 записей логов (B1-B8) |

---

## Миграции

Начальная миграция создаёт все 3 таблицы, индексы и FK-ограничения. Alembic используется для версионирования схемы.

```python
# alembic/versions/001_initial_schema.py
# Создание таблиц: student_profiles, personalized_tracks, qa_reports, generation_logs
# Создание индексов
# Создание FK constraints с ON DELETE CASCADE для profile_id и track_id
```

**ON DELETE поведение:**
- `student_profiles` удаление → CASCADE на `personalized_tracks` и `qa_reports`
- `qa_reports` удаление → SET NULL на `personalized_tracks.qa_report_id`
- `personalized_tracks` удаление → CASCADE на `generation_logs`