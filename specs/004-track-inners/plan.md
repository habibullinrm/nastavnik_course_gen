# Implementation Plan: Просмотр внутреннего содержимого трека

**Branch**: `004-track-inners` | **Date**: 2026-02-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-track-inners/spec.md`

## Summary

Реализовать страницу детального просмотра трека с вкладками для каждого шага
пайплайна (B2–B8): компетенции, ЗУН-матрица, дерево учебных единиц, PBL-сценарии,
расписание и метаданные. Все данные уже хранятся в `track_data: JSONB` существующей
модели `PersonalizedTrack`. Задача — написать React-компоненты для читаемого
отображения этих данных. Дополнительно: добавить страницу профиля со ссылкой на
последний трек (US4) и один новый backend endpoint.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 async (backend); Next.js 14+, Tailwind CSS (frontend)
**Storage**: PostgreSQL 16 (asyncpg) — JSONB для track_data (без изменений схемы БД)
**Testing**: pytest (backend), нет frontend unit-тестов (вне scope)
**Target Platform**: Linux server (Docker), web browser
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Переключение вкладок < 0.5 сек (client-side, без сетевых запросов)
**Constraints**: Данные для всех вкладок загружаются одним запросом. Null/undefined в track_data не должны вызывать ошибок рендеринга.
**Scale/Scope**: Один разработчик, 1–100 треков в БД, инструмент-исследователь

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Принцип | Статус | Комментарий |
|---------|--------|-------------|
| I. Container Isolation | ✅ PASS | Frontend в `frontend`, backend в `backend`, без изменений docker-compose |
| II. Technology Stack | ✅ PASS | Next.js + Tailwind (frontend), FastAPI (backend) — стек не меняется |
| III. Async-First | ✅ PASS | Один новый endpoint использует `async def`; fetch на фронтенде неблокирующий |
| IV. Russian Documentation | ✅ PASS | Все docstring, комментарии, specs на русском |
| V. DeepSeek as LLM | N/A | Фича не использует LLM-запросы |

**Verdict**: ✅ Все применимые принципы соблюдены. Можно приступать к реализации.

## Project Structure

### Documentation (this feature)

```text
specs/004-track-inners/
├── plan.md              # Этот файл
├── research.md          # Phase 0: схемы track_data, состояние компонентов
├── data-model.md        # Phase 1: TypeScript-типы, связи сущностей
├── quickstart.md        # Phase 1: сценарии проверки, структура файлов
├── contracts/
│   └── api.md           # Phase 1: API endpoints, схемы запросов/ответов
└── tasks.md             # Phase 2: задачи (создаётся /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── profiles.py          # + GET /api/profiles/{id}/last-track
│   └── schemas/
│       └── student_profile.py   # + LastTrackResponse
└── tests/
    └── unit/
        └── test_profiles_api.py # тест нового endpoint

frontend/
├── src/
│   ├── app/
│   │   ├── tracks/
│   │   │   └── [trackId]/
│   │   │       └── page.tsx         # переработать: добавить TabNav, подключить компоненты
│   │   └── profiles/
│   │       ├── [profileId]/
│   │       │   └── page.tsx         # создать: детальный просмотр профиля + ссылка на трек
│   │       └── page.tsx             # обновить: ссылки на /profiles/[id]
│   ├── components/
│   │   └── Track/
│   │       ├── TrackTabs.tsx         # новый: TabBar навигация
│   │       ├── TrackMetadata.tsx     # замена заглушки: статусы B1–B8
│   │       ├── CompetencyList.tsx    # новый: B2 компетенции
│   │       ├── KSAMatrix.tsx         # новый: B3 ЗУН-матрица
│   │       ├── LearningTree.tsx      # замена TreeView заглушки: B4+B5 дерево
│   │       ├── LessonBlueprints.tsx  # новый: B6 PBL-сценарии
│   │       ├── WeeklySchedule.tsx    # замена заглушки: B7 расписание
│   │       └── EmptySection.tsx      # новый: переиспользуемая заглушка
│   └── types/
│       ├── index.ts                  # расширить: TrackData типы
│       └── track.ts                  # новый: детальные типы track_data разделов
└── tests/                            # (нет frontend-тестов в scope)
```

**Structure Decision**: Web application (Option 2). Backend — тонкое дополнение (1 endpoint). Frontend — основная работа: 6 новых компонентов + 3 страницы.

## Complexity Tracking

> Нет нарушений конституции. Таблица не заполняется.
