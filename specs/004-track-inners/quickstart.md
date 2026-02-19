# Quickstart: Просмотр внутреннего содержимого трека

**Feature**: 004-track-inners
**Date**: 2026-02-18

## Цель

После реализации исследователь должен мочь открыть страницу любого
completed-трека и увидеть все выходы B2–B7 в читаемом формате.

## Сценарий проверки (вручную)

### Предусловие

1. Есть хотя бы один `completed` трек в базе данных.
2. Запустить приложение: `docker compose up`.

### Шаги

1. Открыть `http://localhost:3000/tracks`.
2. Нажать на название трека — перейти на `/tracks/<uuid>`.
3. Убедиться, что вкладка **Метаданные** открыта по умолчанию:
   - Видны статусы шагов B1–B8 (завершён/ошибка/не выполнен).
   - Видно общее время генерации.
4. Переключиться на **Компетенции**:
   - Видны карточки компетенций: название + описание.
   - Если шаг B2 не выполнялся — сообщение «Компетенции не сгенерированы».
5. Переключиться на **ЗУН-матрица**:
   - Для каждой компетенции — раскрывающийся список Знаний, Умений, Навыков.
6. Переключиться на **Учебные единицы**:
   - Дерево: Уровни → Кластеры → Единицы.
   - Каждый узел показывает тип (theory/practice/automation) и длительность.
   - Checkpoint-узлы визуально выделены.
7. Переключиться на **PBL-сценарии**:
   - Список LessonBlueprint: формулировка проблемы + задачи.
8. Переключиться на **Расписание**:
   - Таблица по неделям с темой и целями.
9. Перейти на `/profiles` → открыть страницу профиля → убедиться в наличии ссылки на последний трек.

### Проверка edge cases

- Открыть трек со статусом `failed`: незаполненные разделы показывают «Ошибка генерации».
- Открыть трек со статусом `generating`: незавершённые разделы показывают «В процессе генерации».
- В профиле без треков: ссылки на трек нет, есть кнопка «Генерировать трек».

## Структура файлов (что создаётся)

```
frontend/src/
├── app/
│   ├── tracks/[trackId]/
│   │   └── page.tsx          — переработанная страница с табами
│   └── profiles/
│       ├── [profileId]/
│       │   └── page.tsx      — страница профиля со ссылкой на трек
│       └── page.tsx          — список профилей (ссылки на /profiles/[id])
├── components/
│   └── Track/
│       ├── TrackTabs.tsx         — навигация между вкладками
│       ├── TrackMetadata.tsx     — метаданные и статусы шагов (замена заглушки)
│       ├── CompetencyList.tsx    — список компетенций B2
│       ├── KSAMatrix.tsx         — ЗУН-матрица B3
│       ├── LearningTree.tsx      — дерево учебных единиц B4+B5 (замена TreeView)
│       ├── LessonBlueprints.tsx  — PBL-сценарии B6
│       ├── WeeklySchedule.tsx    — расписание B7 (замена заглушки)
│       └── EmptySection.tsx      — переиспользуемая заглушка
└── types/
    └── track.ts                  — TypeScript-типы для track_data разделов

backend/src/
├── api/
│   └── profiles.py           — добавить GET /api/profiles/{id}/last-track
└── schemas/
    └── student_profile.py    — добавить LastTrackResponse схему
```

## Сборка и запуск

```bash
# Запустить все сервисы
docker compose up

# Или пересобрать только frontend
docker compose build frontend && docker compose up frontend
```

## Ключевые зависимости

| Компонент | Зависит от | Данные |
|-----------|------------|--------|
| CompetencyList | track.track_data.competency_set | B2 |
| KSAMatrix | track.track_data.ksa_matrix | B3 |
| LearningTree | track.track_data.learning_units + hierarchy | B4+B5 |
| LessonBlueprints | track.track_data.lesson_blueprints | B6 |
| WeeklySchedule | track.track_data.schedule | B7 |
| TrackMetadata | track.generation_metadata + track.status | общая |
