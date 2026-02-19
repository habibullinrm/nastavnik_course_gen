# Research: Просмотр внутреннего содержимого трека

**Feature**: 004-track-inners
**Date**: 2026-02-18
**Phase**: 0 — Research

## Решения и обоснования

### 1. Структура track_data (B1–B8)

**Decision**: Данные всех шагов хранятся в JSONB-поле `track_data` модели `PersonalizedTrack` под фиксированными ключами.

**Rationale**: Исследование реального кода ml/src/services/ и ml/src/schemas/ подтвердило следующую структуру:

```
track_data:
├── validated_profile    (B1) — обогащённый профиль
├── competency_set       (B2) — набор компетенций
├── ksa_matrix           (B3) — ЗУН-матрица
├── learning_units       (B4) — учебные единицы
├── hierarchy            (B5) — иерархия уровней
├── lesson_blueprints    (B6) — PBL-сценарии (lesson blueprints)
├── schedule             (B7) — расписание занятий
└── validation           (B8) — результаты валидации
```

**Ключ B6**: `lesson_blueprints` (не `pbl_tasks`) — уточнено по реальным схемам.

### 2. Детализация схем данных

#### B2 — competency_set
```
competency_set:
  competencies[]:
    id, title, description, related_task_ids[], level
  integral_competency_id: str
  competency_task_map: { competency_id → task_ids[] }
  task_competency_map: { task_id → competency_ids[] }
```

#### B3 — ksa_matrix
```
ksa_matrix:
  knowledge_items[]:
    id, title, description, related_competency_ids[], complexity_level, is_prerequisite
  skill_items[]:
    id, title, description, related_competency_ids[], practice_count_required
  habit_items[]:
    id, title, description, related_competency_ids[], automation_level
  dependency_graph[]:
    from_id, to_id, relation_type
```

#### B4 — learning_units
```
learning_units:
  theory_units[]:
    id, title, description, ksa_item_ids[], duration_minutes, format
  practice_units[]:
    id, title, description, ksa_item_ids[], duration_minutes, practice_type
  automation_units[]:
    id, title, description, ksa_item_ids[], duration_minutes, repetition_count
  clusters[]:
    id, title, unit_ids[]
```

#### B5 — hierarchy
```
hierarchy:
  levels[]:
    level_number, title, cluster_ids[], duration_weeks
  unit_sequence[]:
    unit_id, unit_type, position, week_number
  time_compression_applied: bool
  total_weeks: int
```

#### B6 — lesson_blueprints
```
lesson_blueprints:
  blueprints[]:
    id, cluster_id, problem_formulation, knowledge_infusions[], practice_tasks[],
    contradictions[], synthesis_tasks[], reflection_questions[], fsm_rules[]
```

#### B7 — schedule
```
schedule:
  weeks[]:
    week_number, level, theme, weekly_goals[], days[]:
      day_of_week, units[]: { unit_id, unit_type, duration_minutes }
    checkpoint: { has_checkpoint, description } | null
  checkpoints[]:
    week_number, type, description, success_criteria[]
  final_assessment: { type, description, criteria[] }
  support_plan: { reminders[], milestones[] }
  progress_milestones[]:
    week_number, milestone_description
```

#### B8 — validation
```
validation:
  overall_valid: bool
  checks[]:
    name, passed, details, severity
  critical_failures[]: str[]
  warnings[]: str[]
  final_status: 'valid' | 'needs_revision' | 'failed'
```

### 3. Состояние существующих frontend-компонентов

**Decision**: Все 4 существующих компонента страницы трека — заглушки. Требуется реализация с нуля.

**Компоненты-заглушки**:
- `TreeView` — выводит raw JSON, нет реального дерева
- `WeeklySchedule` — пустой placeholder «в разработке»
- `TrackMetadata` — пустой placeholder «в разработке»
- `FieldUsage` — пустой placeholder «в разработке»

**Новые компоненты** (не существуют):
- `CompetencyList` — нет
- `KSAMatrix` — нет
- `LessonBlueprints` (PBL) — нет

### 4. Архитектура страницы трека

**Decision**: Табовая навигация с client-side переключением без дополнительных API-запросов.

**Rationale**: Все данные уже загружены в `track_data` при первом запросе. Переключение вкладок — чисто клиентская операция. Соответствует SC-004 (переключение < 0.5 сек).

**Вкладки**:
1. **Метаданные** — статусы шагов B1–B8, общая информация
2. **Компетенции** — B2 competency_set
3. **ЗУН-матрица** — B3 ksa_matrix
4. **Учебные единицы** — B4+B5 дерево
5. **PBL-сценарии** — B6 lesson_blueprints
6. **Расписание** — B7 schedule

### 5. Обработка null/undefined данных

**Decision**: Для каждой вкладки реализовать guard-компонент с информативным сообщением-заглушкой.

**Паттерн**:
```tsx
if (!track_data?.competency_set) {
  return <EmptySection message="Компетенции не сгенерированы" step="B2" />
}
```

Для треков в статусе `generating`: вкладки завершённых шагов показывают данные, незавершённые — «В процессе генерации».

### 6. Ссылка на трек со страницы профиля (US4)

**Decision**: Добавить ссылку на последний трек в существующий компонент страницы профиля.

**Реализация**: Endpoint `GET /api/tracks?profile_id=<id>&limit=1&sort=created_at:desc` уже существует в backend. Необходимо добавить запрос при загрузке профиля.

**Alternatives considered**: Добавить denormalized `last_track_id` в `StudentProfile` — отвергнуто как избыточное.

### 7. Навигация к треку

**Decision**: Страница трека `/tracks/[trackId]` уже существует. Нужно только добавить ссылку и убедиться, что вкладки реализованы.

**Существующий маршрут**: `frontend/src/app/tracks/[trackId]/page.tsx`
