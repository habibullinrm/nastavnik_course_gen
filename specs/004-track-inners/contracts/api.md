# API Contracts: Просмотр внутреннего содержимого трека

**Feature**: 004-track-inners
**Date**: 2026-02-18

## Существующие endpoints (используются без изменений)

### GET /api/tracks/{track_id}

Возвращает полный `PersonalizedTrack` включая весь `track_data`.

**Response** (существующая схема):
```json
{
  "id": "uuid",
  "profile_id": "uuid",
  "qa_report_id": null,
  "track_data": {
    "validated_profile": {...},
    "competency_set": {
      "competencies": [
        {"id": "c1", "title": "...", "description": "...", "related_task_ids": [], "level": "..."}
      ],
      "integral_competency_id": "c0",
      "competency_task_map": {},
      "task_competency_map": {}
    },
    "ksa_matrix": {
      "knowledge_items": [...],
      "skill_items": [...],
      "habit_items": [...],
      "dependency_graph": [...]
    },
    "learning_units": {...},
    "hierarchy": {...},
    "lesson_blueprints": {"blueprints": [...]},
    "schedule": {...},
    "validation": {...}
  },
  "generation_metadata": {...},
  "algorithm_version": "1.0",
  "validation_b8": null,
  "status": "completed",
  "error_message": null,
  "generation_duration_sec": 42.5,
  "batch_index": null,
  "created_at": "2026-02-18T10:00:00Z",
  "updated_at": "2026-02-18T10:00:42Z"
}
```

**Используется**: страницей `/tracks/[trackId]` — уже реализовано.

---

### GET /api/tracks?profile_id={profile_id}&limit=1

Возвращает список треков для профиля (самый новый сверху по умолчанию).

**Используется**: для US4 — получение последнего трека профиля.

**Response** (существующая схема):
```json
[
  {
    "id": "uuid",
    "profile_id": "uuid",
    "topic": "Математическая логика",
    "algorithm_version": "1.0",
    "status": "completed",
    "generation_duration_sec": 42.5,
    "created_at": "2026-02-18T10:00:00Z"
  }
]
```

---

## Новый endpoint (для US4)

### GET /api/profiles/{profile_id}/last-track

Возвращает краткую информацию о последнем треке профиля.

**Path params**:
- `profile_id: UUID` — идентификатор профиля

**Response 200**:
```json
{
  "track_id": "uuid",
  "status": "completed",
  "created_at": "2026-02-18T10:00:00Z"
}
```

**Response 404** (трек не найден):
```json
{
  "detail": "Для этого профиля треки не найдены"
}
```

**Implementation note**: Можно реализовать как тонкий wrapper над существующим `GET /api/tracks?profile_id=X&limit=1`. Возвращает первый элемент или 404.

---

## Frontend API вызовы

### Страница /tracks/[trackId]

```typescript
// Загрузка трека — единственный запрос, все данные в одном объекте
const track = await fetchTrack(trackId)  // GET /api/tracks/{trackId}
// После загрузки — только client-side переключение вкладок
```

### Страница /profiles/[profileId]

```typescript
// Загрузка последнего трека для показа ссылки (US4)
const lastTrack = await fetchLastTrack(profileId)  // GET /api/profiles/{profileId}/last-track
```

---

## Схема данных для компонентов

Страница `/tracks/[trackId]/page.tsx` передаёт props в дочерние компоненты:

```typescript
// CompetencyList
<CompetencyList data={track.track_data?.competency_set} />

// KSAMatrix
<KSAMatrix data={track.track_data?.ksa_matrix} />

// LearningTree (дерево B4+B5)
<LearningTree
  units={track.track_data?.learning_units}
  hierarchy={track.track_data?.hierarchy}
/>

// LessonBlueprints (PBL)
<LessonBlueprints data={track.track_data?.lesson_blueprints} />

// WeeklySchedule (B7)
<WeeklySchedule data={track.track_data?.schedule} />

// TrackMetadata (статусы шагов)
<TrackMetadata
  track={track}
  metadata={track.generation_metadata}
/>
```
