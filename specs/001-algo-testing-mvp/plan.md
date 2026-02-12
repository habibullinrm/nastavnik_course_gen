# Implementation Plan: Сервис тестирования алгоритма генерации учебных треков

**Branch**: `001-algo-testing-mvp` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-algo-testing-mvp/spec.md`

## Summary

Внутренний веб-сервис для тестирования Фазы B (генерация персонализированных учебных треков). Позволяет загрузить JSON-профиль учащегося (`StudentProfile`), выполнить полный pipeline B1-B8 через DeepSeek API, просмотреть результат в древовидной структуре, запустить пакетную генерацию (1–100 версий) и оценить стабильность алгоритма через коэффициент различия версий (CDV). Профили и треки персистятся в PostgreSQL.

## Technical Context

**Language/Version**: Python 3.11+ (backend, ML), TypeScript/Next.js (frontend)
**Primary Dependencies**: FastAPI, Next.js 14+, Tailwind CSS, httpx (async HTTP), Pydantic v2, SQLAlchemy 2.0 (async), alembic
**Storage**: PostgreSQL 16 (asyncpg)
**Testing**: pytest + pytest-asyncio (backend/ML), vitest + Playwright (frontend)
**Target Platform**: Docker containers (Linux), Docker Compose для оркестрации
**Project Type**: Web application (frontend + backend + ml + db — 4 контейнера)
**Performance Goals**: Однопользовательский сервис; один pipeline B1-B8 = 20–60 LLM-вызовов; пакетная генерация до 100 запусков
**Constraints**: Лимиты DeepSeek API (rate limits, token limits); async-first для всех I/O; время одной генерации зависит от LLM (~2–10 мин)
**Scale/Scope**: 1 разработчик-пользователь, ~8 страниц UI, ~15 API-эндпоинтов

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Принцип | Статус | Обоснование |
|---|---------|--------|-------------|
| I | Container Isolation | ✅ PASS | 4 контейнера: `frontend` (Next.js), `backend` (FastAPI), `ml` (FastAPI), `db` (PostgreSQL). Каждый сервис — отдельный Dockerfile + docker-compose.yml. Взаимодействие через HTTP. |
| II | Technology Stack | ✅ PASS | Frontend: Next.js + Tailwind CSS. Backend + ML: Python + FastAPI. БД: PostgreSQL. Оркестрация: Docker Compose. Новых runtime-зависимостей не добавляется. |
| III | Async-First | ✅ PASS | Все эндпоинты FastAPI — `async def`. БД через asyncpg. Запросы к DeepSeek через `httpx.AsyncClient`. Frontend — неблокирующие fetch-вызовы. |
| IV | Russian Documentation | ✅ PASS | Docstring в Google Docstring формате на русском. Коммиты на русском. Спецификации на русском. JSDoc на русском. Имена переменных/функций на английском. |
| V | DeepSeek as LLM Provider | ✅ PASS | ML-сервис отправляет запросы к DeepSeek API. Промпты: инструкция + входные данные + формат выхода (TS-интерфейс) + критерии качества + примеры. Ключи API в переменных окружения. Retry с backoff при недоступности. |

**Результат**: все 5 принципов конституции соблюдены. Нарушений нет.

## Project Structure

### Documentation (this feature)

```text
specs/001-algo-testing-mvp/
├── plan.md              # Этот файл
├── research.md          # Phase 0: исследование технологий
├── data-model.md        # Phase 1: модель данных
├── quickstart.md        # Phase 1: быстрый старт
├── contracts/           # Phase 1: API-контракты
│   ├── backend-api.yaml     # OpenAPI — backend endpoints
│   └── ml-api.yaml          # OpenAPI — ML service endpoints
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/              # SQLAlchemy async models (StudentProfile, PersonalizedTrack, QAReport)
│   ├── schemas/             # Pydantic v2 request/response schemas
│   ├── services/            # Бизнес-логика: профили, треки, QA, экспорт
│   ├── api/                 # FastAPI routers (profiles, tracks, qa, export)
│   └── core/                # Конфигурация, database engine, dependencies
├── alembic/                 # Миграции БД
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── Dockerfile
└── pyproject.toml

ml/
├── src/
│   ├── pipeline/            # Шаги B1-B8 (отдельный модуль на каждый шаг)
│   │   ├── b1_validate.py
│   │   ├── b2_competencies.py
│   │   ├── b3_ksa_matrix.py
│   │   ├── b4_learning_units.py
│   │   ├── b5_hierarchy.py
│   │   ├── b6_problem_formulations.py
│   │   ├── b7_schedule.py
│   │   └── b8_validation.py
│   ├── prompts/             # Шаблоны промптов для DeepSeek
│   ├── services/            # DeepSeek client, pipeline orchestrator, CDV calculator
│   ├── api/                 # FastAPI routers (pipeline, health)
│   ├── schemas/             # Pydantic-модели промежуточных и финальных структур
│   └── core/                # Конфигурация, retry logic
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── page.tsx                 # Главная: загрузка JSON
│   │   ├── tracks/
│   │   │   ├── [id]/page.tsx        # Просмотр трека (дерево)
│   │   │   └── generate/page.tsx    # Прогресс генерации
│   │   ├── qa/
│   │   │   ├── page.tsx             # Запуск пакетной генерации
│   │   │   └── [id]/page.tsx        # QA-отчёт: CDV, стабильность
│   │   └── profiles/
│   │       └── [id]/page.tsx        # Просмотр загруженного профиля
│   ├── components/          # React-компоненты
│   │   ├── TreeView/                # Древовидное отображение трека
│   │   ├── ProfileUpload/           # Загрузка JSON
│   │   ├── QAReport/                # Таблица CDV, рекомендации
│   │   ├── GenerationProgress/      # Прогресс-бар B1-B8
│   │   └── ExportButton/            # Экспорт JSON
│   ├── services/            # API-клиенты (fetch wrappers)
│   └── types/               # TypeScript типы
├── tests/
├── Dockerfile
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json

docker-compose.yml           # Оркестрация: frontend, backend, ml, db
.env.example                 # Переменные окружения (DEEPSEEK_API_KEY и др.)
```

**Structure Decision**: Выбрана структура веб-приложения с 4 контейнерами согласно Принципу I конституции. Backend отвечает за хранение данных (профили, треки, отчёты) и оркестрацию. ML-сервис изолирует pipeline B1-B8 и взаимодействие с DeepSeek. Frontend — SPA на Next.js для просмотра результатов.

## Complexity Tracking

> Нарушений конституции нет. Таблица пуста.

*Пусто — все принципы соблюдены.*