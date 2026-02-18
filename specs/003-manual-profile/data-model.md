
# Data Model: Manual Profile Editor (003-manual-profile)

## Существующие сущности (без изменений)

### StudentProfile (PostgreSQL)

```sql
student_profiles
├── id                UUID PRIMARY KEY
├── data              JSONB           -- полный профиль (StudentProfileInput)
├── filename          VARCHAR(255)    -- имя файла; для форм: "form-{topic_slug}"
├── validation_result JSONB           -- { valid, errors[], warnings[] }
├── topic             VARCHAR(500)    -- извлечённый topic для индексации
├── experience_level  VARCHAR(50)     -- zero/beginner/intermediate/advanced
├── created_at        TIMESTAMPTZ
└── updated_at        TIMESTAMPTZ
```

---

## Вложенные типы (StudentProfileInput)

Уже определены в `backend/src/schemas/student_profile.py`.
Здесь — TypeScript-эквиваленты для frontend.

```typescript
interface Task {
  id: string            // "t1", "t2", ...
  description: string
  complexity_rank: number  // 1 = простейшая, N = вершина мастерства
}

interface Subtask {
  id: string
  description: string
  parent_task_id: string   // → Task.id (обычно peak_task_id)
  required_skills: string[]
  required_knowledge: string[]
}

interface Barrier {
  id: string
  description: string
  barrier_type: "conceptual" | "procedural" | "motivational"
  related_task_id: string
}

interface Concept {
  id: string
  term: string
  confusion_description: string
}

interface ScheduleDay {
  day_of_week: "monday"|"tuesday"|"wednesday"|"thursday"|"friday"|"saturday"|"sunday"
  available_minutes: number
}

interface PracticeWindow {
  time_of_day: "morning" | "afternoon" | "evening"
  duration_minutes: number
  device: "phone" | "laptop" | "tablet"
}

interface SuccessCriterion {
  id: string
  description: string
  metric: string       // "accuracy >= 0.8", "exam_grade >= 4"
  measurable: boolean
}
```

---

## Состояние формы (frontend)

```typescript
interface ProfileFormState {
  // ── Блок 0: Тема ──────────────────────────────────────────
  topic: string                   // 🔴 CRITICAL
  subject_area: string            // 🔴 CRITICAL
  topic_scope: string             // 🟡 IMPORTANT

  // ── Блок 1: Контекст и мотивация ──────────────────────────
  role: string                    // 🟡 IMPORTANT
  experience_level: "zero"|"beginner"|"intermediate"|"advanced"|""  // 🔴
  formal_education: string        // 🟢 OPTIONAL
  identified_risks: string[]      // 🟡 IMPORTANT
  novice_mode: boolean            // derived: experience_level in ["zero","beginner"]
  motivation_external: string     // 🟡 IMPORTANT
  motivation_internal: string     // 🟢 OPTIONAL
  goal_type: "applied"|"fundamental"|"mixed"|""  // 🟡 IMPORTANT
  has_deadline: boolean           // 🟡 IMPORTANT
  deadline_date: string           // 🟡 IMPORTANT (ISO date, "" если нет)
  desired_outcomes: string[]      // 🔴 CRITICAL
  target_context: string          // 🟡 IMPORTANT
  outcome_source: "user"|"system_suggested"|"mixed"|""  // 🟢 OPTIONAL

  // ── Блок 2: Учебные задачи ────────────────────────────────
  target_tasks: Task[]            // 🔴 CRITICAL
  tasks_source: "user"|"system_generated"|"mixed"|""  // 🟢
  task_hierarchy: Task[]          // 🔴 CRITICAL (reordered)
  easiest_task_id: string         // 🔴 CRITICAL
  peak_task_id: string            // 🔴 CRITICAL
  subtasks: Subtask[]             // 🔴 CRITICAL
  subtasks_source: "user"|"system_generated"|"mixed"|""  // 🟢
  already_known_subtasks: string[]  // 🟡 IMPORTANT
  primary_context: string         // 🟡 IMPORTANT
  secondary_context: string       // 🟢 OPTIONAL
  context_type: "academic"|"professional"|"personal"|"general"|""  // 🟡

  // ── Блок 3: Диагностика ───────────────────────────────────
  current_approach: string        // 🟡 IMPORTANT
  approach_gaps: string[]         // 🟡 IMPORTANT
  diagnostic_result: "no_knowledge"|"misconceptions"|"partial"|"solid_base"|""  // 🔴
  key_barriers: Barrier[]         // 🟡 IMPORTANT
  barriers_source: "user"|"system_suggested"|"auto_generated"|""  // 🟢
  confusing_concepts: Concept[]   // 🔴 CRITICAL
  concepts_source: "user"|"auto_generated"|""  // 🟢
  theory_format_preference: "visual_schemas"|"examples_first"|"video"|"discussion"|"text_formulas"|"mixed"|""  // 🟡
  theory_format_details: string   // 🟢 OPTIONAL
  best_material_reference: string // 🟢 OPTIONAL

  // ── Блок 4: Практика ──────────────────────────────────────
  instruction_format: string[]    // 🟡 IMPORTANT
  feedback_type: string[]         // 🟡 IMPORTANT
  practice_format: string[]       // 🟡 IMPORTANT
  daily_practice_minutes: number  // 🟡 IMPORTANT
  practice_windows: PracticeWindow[]  // 🟢 OPTIONAL
  needs_reminder: boolean         // 🟢 OPTIONAL
  mastery_signals: string[]       // 🟢 OPTIONAL
  support_tools: string[]         // 🟢 OPTIONAL

  // ── Блок 5: Организация ───────────────────────────────────
  weekly_hours: number            // 🔴 CRITICAL
  schedule: ScheduleDay[]         // 🟡 IMPORTANT
  learning_format: "self_paced"|"mentored"|"group"|"mixed"|""  // 🟡
  support_channel: string         // 🟢 OPTIONAL

  // ── Критерии успеха ───────────────────────────────────────
  success_criteria: SuccessCriterion[]  // 🔴 CRITICAL
}
```

### Значения по умолчанию

```typescript
const DEFAULT_PROFILE: ProfileFormState = {
  topic: "", subject_area: "", topic_scope: "",
  role: "", experience_level: "", formal_education: "",
  identified_risks: [], novice_mode: false,
  motivation_external: "", motivation_internal: "",
  goal_type: "", has_deadline: false, deadline_date: "",
  desired_outcomes: [], target_context: "", outcome_source: "user",
  target_tasks: [], tasks_source: "user",
  task_hierarchy: [], easiest_task_id: "", peak_task_id: "",
  subtasks: [], subtasks_source: "user", already_known_subtasks: [],
  primary_context: "", secondary_context: "", context_type: "",
  current_approach: "", approach_gaps: [], diagnostic_result: "",
  key_barriers: [], barriers_source: "user",
  confusing_concepts: [], concepts_source: "user",
  theory_format_preference: "examples_first",
  theory_format_details: "", best_material_reference: "",
  instruction_format: ["checklist"],
  feedback_type: ["error_with_explanation"],
  practice_format: ["compare_with_standard"],
  daily_practice_minutes: 10, practice_windows: [],
  needs_reminder: true, mastery_signals: [], support_tools: ["progress_tracker"],
  weekly_hours: 5, schedule: [], learning_format: "", support_channel: "",
  success_criteria: [],
}
```

---

## Правила валидации

### Frontend (блокируют отправку)

| Правило | Поля |
|---|---|
| Непустое значение | topic, subject_area, experience_level, diagnostic_result |
| Массив ≥ 1 элемента | desired_outcomes, target_tasks, subtasks, confusing_concepts, success_criteria |
| ID из target_tasks | easiest_task_id, peak_task_id |
| Положительное число | weekly_hours > 0 |

### Backend (Pydantic)

Существующий `StudentProfileInput` + `validate_profile()` в `profile_service.py`.