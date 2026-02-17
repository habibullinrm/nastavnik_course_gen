# Implementation Plan: Сервис тестирования алгоритма генерации учебных треков

**Branch**: `001-algo-testing-mvp` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-algo-testing-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

**Основное требование**: Реализовать MVP-сервис для тестирования и отладки алгоритма генерации персонализированных учебных треков (Phase B pipeline: шаги B1-B8). Система должна принимать JSON-профиль учащегося, выполнять полный цикл генерации через DeepSeek API, сохранять все промежуточные результаты в базу данных для отладки и предоставлять web-интерфейс для просмотра результатов, пакетной генерации и контроля качества (CDV-метрики).

**Технический подход**: Микросервисная архитектура с 4 Docker-контейнерами (frontend, backend, ml, db). Backend (FastAPI) управляет профилями и треками, ML-сервис (FastAPI) выполняет pipeline B1-B8 через DeepSeek API с retry механизмом, Frontend (Next.js) обеспечивает UI для загрузки, мониторинга генерации и просмотра результатов. PostgreSQL хранит профили, треки и детальные audit logs всех промежуточных шагов с retention policy 30 дней. Все сервисы используют async-first подход (asyncpg, httpx, async def endpoints).

**Дополнительные возможности (Phase 4a)**: Real-time прогресс генерации через SSE с DB polling (именованные события: step_update, complete, cancelled, error), ручная остановка генерации (cancel → cancelling → cancelled), batch-генерация N треков (2-5) с общим batch_id. Background tasks через asyncio.create_task, POST /generate возвращает HTTP 202 Accepted немедленно.

## Technical Context

**Language/Version**: Python 3.11+ (backend, ml), TypeScript 5.3+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.109+, SQLAlchemy 2.0 (async), asyncpg 0.29+, Pydantic 2.5+, httpx 0.26+ (async HTTP), Alembic 1.13+ (migrations)
- ML: FastAPI 0.109+, httpx 0.26+ (DeepSeek client), Pydantic 2.5+, sse-starlette 1.8+ (SSE), rich 13.0+ (logging), networkx 3.0+ (graph analysis)
- Frontend: Next.js 14.1+, React 18.2+, Tailwind CSS 3.4+, Playwright 1.58+ (E2E tests)

**Storage**: PostgreSQL 16 (asyncpg driver) — хранение StudentProfile, PersonalizedTrack, QAReport, GenerationLog (audit) с retention policy 30 дней для логов

**Testing**:
- Backend/ML: pytest 7.4+ с pytest-asyncio 0.21+ (unit, integration, E2E tests)
- Frontend: Playwright 1.58+ (E2E тесты UI сценариев)
- Code quality: black 23.12+, ruff 0.1.9+ (Python), eslint (TypeScript)

**Target Platform**: Linux server (Docker Compose orchestration), разработка в локальных контейнерах, деплой в production-контейнеры

**Project Type**: Web application (frontend + backend + ml) — Option 2 из шаблона

**Performance Goals**:
- Генерация одного трека: 2-5 минут (исключая LLM API время) — баланс между качеством валидации/logging и UX
- Валидация JSON профиля: < 2 секунд для файлов до 100KB
- Пакетная генерация: последовательная (N × время генерации), параллелизация вне скоупа MVP

**Constraints**:
- LLM API retry: 3 попытки с exponential backoff (1s, 2s, 4s) при сбоях
- Database retention: 30 дней для GenerationLog, бессрочно для профилей/треков
- Target reliability: 95%+ при нормальной работе DeepSeek API
- Storage footprint: ~3GB для 30 дней audit logs (100 генераций/день)

**Scale/Scope**:
- Внутренний инструмент для 1 разработчика (no мультитенантность)
- Pipeline: 8 шагов (B1-B8) × 20-60 LLM вызовов на трек
- Пакетная генерация: до 100 версий трека из одного профиля
- 4 Docker сервиса: frontend, backend, ml, db

## API Endpoints for Step Testing

**Назначение**: Эндпоинты для изолированного тестирования отдельных шагов B1-B8 без запуска полного пайплайна. Позволяют быстро отлаживать промпты и проверять изменения в логике отдельных шагов.

**Базовый URL**: `http://localhost:8002/steps/`

**Доступные эндпоинты**:
- `POST /steps/b1` — B1: Profile Validation and Enrichment
- `POST /steps/b2` — B2: Competency Formulation
- `POST /steps/b3` — B3: KSA Matrix (Knowledge-Skills-Habits)
- `POST /steps/b4` — B4: Learning Units Design
- `POST /steps/b5` — B5: Hierarchy and Levels
- `POST /steps/b6` — B6: Problem Formulations (Lesson Blueprints)
- `POST /steps/b7` — B7: Schedule Assembly
- `POST /steps/b8` — B8: Track Validation

**Request format** (общий для всех эндпоинтов):
```json
{
  "use_mock": true,  // true = MockLLMClient, false = DeepSeekClient
  "inputs": {
    // Структура зависит от шага (см. примеры ниже)
  }
}
```

**Response format** (общий для всех эндпоинтов):
```json
{
  "step_name": "B1",
  "success": true,
  "output": {
    // OutputSchema шага в виде dict
  },
  "metadata": {
    "tokens_used": 1193,
    "duration_ms": 0.24,
    "model": "mock-llm"
  },
  "error": null  // Описание ошибки при success=false
}
```

**Input structures по шагам**:

**B1** (Profile Validation):
```json
{
  "inputs": {
    "profile": {
      "topic": "...",
      "subject_area": "...",
      "experience_level": "beginner",
      // ... полный ProfileRequest
    }
  }
}
```

**B2** (Competency Formulation):
```json
{
  "inputs": {
    "validated_profile": {
      // ... полный вывод B1 (ValidatedStudentProfile)
    }
  }
}
```

**B3** (KSA Matrix):
```json
{
  "inputs": {
    "profile": {...},        // original profile
    "competencies": {...}    // вывод B2
  }
}
```

**B4** (Learning Units):
```json
{
  "inputs": {
    "ksa_matrix": {...}  // вывод B3
  }
}
```

**B5** (Hierarchy):
```json
{
  "inputs": {
    "learning_units": {...},       // вывод B4
    "time_budget_minutes": 1800,
    "estimated_weeks": 6
  }
}
```

**B6** (Problem Formulations):
```json
{
  "inputs": {
    "clusters": [...],  // из B4.clusters
    "units": {...}      // из B4 (theory + practice units)
  }
}
```

**B7** (Schedule Assembly):
```json
{
  "inputs": {
    "hierarchy": {...},     // вывод B5
    "blueprints": {...},    // вывод B6
    "profile": {...},       // original profile
    "total_weeks": 6
  }
}
```

**B8** (Track Validation):
```json
{
  "inputs": {
    "complete_track": {
      "validated_profile": {...},  // B1
      "competencies": {...},        // B2
      "ksa_matrix": {...},          // B3
      "learning_units": {...},      // B4
      "hierarchy": {...},           // B5
      "blueprints": {...},          // B6
      "schedule": {...}             // B7
    },
    "profile": {...},  // original profile
    "max_retries": 3
  }
}
```

**Примеры использования**:

1. **Тестирование промпта B1 с mock LLM** (~0.2ms):
```bash
curl -X POST http://localhost:8002/steps/b1 \
  -H "Content-Type: application/json" \
  -d '{
    "use_mock": true,
    "inputs": {
      "profile": {
        "topic": "Python backend",
        "experience_level": "beginner",
        "weekly_hours": 5
      }
    }
  }'
```

2. **Тестирование промпта B2 с реальным DeepSeek** (~40s):
```bash
curl -X POST http://localhost:8002/steps/b2 \
  -H "Content-Type: application/json" \
  -d '{
    "use_mock": false,
    "inputs": {
      "validated_profile": {...}  // загрузите из B1 output
    }
  }'
```

3. **Цепочка тестов B1→B2→B3**:
```bash
# Шаг 1: B1
b1_out=$(curl -s -X POST http://localhost:8002/steps/b1 \
  -H "Content-Type: application/json" \
  -d @profile.json | jq '.output')

# Шаг 2: B2
b2_out=$(curl -s -X POST http://localhost:8002/steps/b2 \
  -H "Content-Type: application/json" \
  -d "{\"use_mock\": true, \"inputs\": {\"validated_profile\": $b1_out}}" \
  | jq '.output')

# Шаг 3: B3
curl -X POST http://localhost:8002/steps/b3 \
  -H "Content-Type: application/json" \
  -d "{\"use_mock\": true, \"inputs\": {\"profile\": $b1_out.original_profile, \"competencies\": $b2_out}}"
```

**Mock fixtures**: Для use_mock=true используются предопределенные ответы из `ml/tests/fixtures/mock_responses/B{1-8}_*.json`. Это позволяет тестировать шаги без реальных API вызовов.

**Доступ через Swagger UI**: `http://localhost:8002/docs` — интерактивная документация со всеми эндпоинтами, схемами и возможностью тестирования прямо в браузере.

**Преимущества**:
- ⚡ Быстрая отладка: тест одного шага занимает ~0.2ms (mock) vs ~326s (полный пайплайн)
- 🔍 Изоляция: можно тестировать один шаг без перезапуска предыдущих
- 🧪 Гибкость: mock или real LLM client
- 📊 Метрики: tokens_used, duration_ms для каждого шага

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Принцип I: Container Isolation

**Статус**: PASS

**Проверка**: Проект использует 4 отдельных Docker-контейнера:
- `frontend` (Next.js) — порт 3000
- `backend` (FastAPI) — порт 8000
- `ml` (FastAPI) — порт 8001 (внутренний), 8002 (внешний)
- `db` (PostgreSQL 16) — порт 5432

Взаимодействие: HTTP через сеть Docker (`nastavnik_network`), нет общей файловой системы или памяти. Каждый сервис имеет собственный Dockerfile и определён в `docker-compose.yml`.

### ✅ Принцип II: Technology Stack

**Статус**: PASS

**Проверка**: Стек технологий соответствует конституции:
- **Frontend**: Next.js 14.1+ + Tailwind CSS 3.4+ ✅
- **Backend**: Python 3.11+ + FastAPI 0.109+ ✅
- **ML-сервис**: Python 3.11+ + FastAPI 0.109+ ✅
- **База данных**: PostgreSQL 16 ✅
- **Оркестрация**: Docker Compose ✅

Дополнительные runtime-зависимости:
- SQLAlchemy 2.0 (async ORM) — стандартный выбор для FastAPI + PostgreSQL
- Alembic 1.13+ (migrations) — стандартный инструмент для SQLAlchemy
- httpx 0.26+ (async HTTP) — стандартный клиент для async FastAPI
- Pydantic 2.5+ (validation) — встроенный в FastAPI
- sse-starlette 1.8+ (SSE) — для real-time прогресса генерации
- networkx 3.0+ (graph analysis) — для анализа зависимостей в pipeline

Все зависимости обоснованы функциональными требованиями (FR-005, FR-006a, FR-006b).

### ✅ Принцип III: Async-First

**Статус**: PASS

**Проверка**:
- Backend endpoints: `async def` в FastAPI (`backend/src/api/*.py`) ✅
- ML endpoints: `async def` в FastAPI (`ml/src/api/*.py`) ✅
- Database queries: `asyncpg` драйвер через SQLAlchemy async engine ✅
- External API calls: `httpx.AsyncClient` для DeepSeek API (`ml/src/services/deepseek_client.py`) ✅
- Frontend: неблокирующие API вызовы через `fetch` в React ✅

Синхронные блокирующие вызовы не используются.

### ✅ Принцип IV: Russian Documentation

**Статус**: PASS

**Проверка**:
- Спецификация: `specs/001-algo-testing-mvp/spec.md` — на русском ✅
- Docstring в Python: Google Docstring на русском (см. `backend/src/models/*.py`, `ml/src/services/*.py`) ✅
- Commit messages: на русском (см. git log) ✅
- JSDoc/комментарии: на русском (в `frontend/src/`) ✅
- Имена переменных/функций: на английском ✅

### ✅ Принцип V: DeepSeek as LLM Provider

**Статус**: PASS

**Проверка**:
- ML-сервис использует DeepSeek API (FR-006b) ✅
- Конфигурация через env vars:
  - `DEEPSEEK_API_KEY` (обязательный)
  - `DEEPSEEK_BASE_URL` (default: https://api.deepseek.com/v1)
  - `DEEPSEEK_MODEL` (default: deepseek-chat)
  - `DEEPSEEK_MAX_RETRIES` (default: 3)
  - `DEEPSEEK_RETRY_BACKOFF_BASE` (default: 2)
- Retry mechanism с exponential backoff реализован (FR-006a) ✅
- Промпты используют структурированный формат (инструкция + входные данные + формат выхода + критерии + примеры) в `ml/src/prompts/b*_prompt.py` ✅

---

**GATE RESULT**: ✅ ALL CHECKS PASSED — можно переходить к Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/                           # Backend API сервис (FastAPI)
├── alembic/                       # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_generation_logs.py
│       └── 003_add_batch_id.py    # batch_id колонка + индекс
├── src/
│   ├── api/                       # FastAPI routers
│   │   ├── health.py              # Health check endpoints
│   │   ├── profiles.py            # StudentProfile CRUD
│   │   ├── tracks.py              # PersonalizedTrack CRUD + generation
│   │   └── logs.py                # GenerationLog viewing
│   ├── core/                      # Configuration & database
│   │   ├── config.py              # Pydantic Settings
│   │   └── database.py            # SQLAlchemy async engine + session
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── student_profile.py     # StudentProfile table
│   │   ├── personalized_track.py  # PersonalizedTrack table
│   │   ├── qa_report.py           # QAReport table
│   │   └── generation_log.py      # GenerationLog table (audit)
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── student_profile.py
│   │   ├── track.py
│   │   └── qa_report.py
│   └── services/                  # Business logic
│       ├── profile_service.py     # Profile validation & CRUD
│       ├── track_service.py       # Track generation orchestration
│       └── field_usage_service.py # Field usage analytics
├── tests/
│   └── e2e/
│       └── test_phase3_e2e.py     # End-to-end backend tests
├── Dockerfile
├── pyproject.toml
└── alembic.ini

ml/                                # ML pipeline сервис (FastAPI)
├── src/
│   ├── api/                       # FastAPI routers
│   │   ├── health.py              # Health check
│   │   └── pipeline.py            # POST /pipeline/run endpoints
│   ├── core/
│   │   └── config.py              # DeepSeek config (env vars)
│   ├── pipeline/                  # Phase B steps (B1-B8)
│   │   ├── b1_validate.py         # Profile validation & enrichment
│   │   ├── b2_competencies.py     # Competencies formulation
│   │   ├── b3_ksa_matrix.py       # KSA (ЗУН) decomposition
│   │   ├── b4_learning_units.py   # Learning units design
│   │   ├── b5_hierarchy.py        # Hierarchy & levels
│   │   ├── b6_problem_formulations.py  # Problem-based formulations
│   │   ├── b7_schedule.py         # Weekly schedule assembly
│   │   └── b8_validation.py       # Track validation
│   ├── prompts/                   # LLM prompts for each step
│   │   ├── b1_prompt.py
│   │   ├── b2_prompt.py
│   │   ├── b3_prompt.py
│   │   ├── b4_prompt.py
│   │   ├── b5_prompt.py
│   │   ├── b6_prompt.py
│   │   ├── b7_prompt.py
│   │   └── b8_prompt.py
│   ├── schemas/                   # Pydantic schemas для pipeline
│   │   ├── pipeline.py            # PipelineRunRequest/Response
│   │   ├── pipeline_steps.py      # B1-B8 input/output schemas
│   │   └── cdv.py                 # CDV metrics for QA
│   └── services/                  # Business logic
│       ├── deepseek_client.py     # DeepSeek API client (httpx)
│       ├── mock_llm_client.py     # Mock client for testing
│       ├── llm_client_factory.py  # Factory для выбора клиента
│       ├── pipeline_orchestrator.py  # Pipeline execution
│       └── step_logger.py         # Logging промежуточных шагов
├── scripts/                       # Development & testing scripts
│   ├── validate_pipeline.py       # Schema & reference validation
│   ├── run_pipeline_mock.py       # Mock mode testing
│   ├── generate_new_track.py      # CLI track generation
│   └── validators/                # Pipeline validation
│       ├── schema_validator.py
│       ├── reference_validator.py
│       └── report_generator.py
├── tests/
│   ├── pipeline/                  # Pipeline tests
│   │   ├── test_schema_validation.py
│   │   └── test_reference_validation.py
│   └── test_mock_llm_client.py
├── Dockerfile
└── pyproject.toml

frontend/                          # Next.js UI (TypeScript + Tailwind)
├── src/
│   ├── app/                       # Next.js 14 App Router
│   │   ├── page.tsx               # Home page
│   │   ├── layout.tsx             # Root layout
│   │   ├── globals.css            # Tailwind styles
│   │   ├── profiles/              # Profile upload & list
│   │   ├── tracks/                # Track detail & list
│   │   │   └── generate/
│   │   │       └── page.tsx       # Генерация (одиночная + batch)
│   │   └── qa/                    # QA report viewing
│   ├── components/                # React components
│   │   ├── ProfileUpload/         # JSON upload component
│   │   ├── TrackMetadata/         # Generation metadata
│   │   ├── TreeView/              # Hierarchical track view
│   │   ├── WeeklySchedule/        # Weekly schedule component
│   │   ├── FieldUsage/            # Field usage indicators
│   │   ├── GenerationProgress/    # SSE progress tracking (real-time B1-B8 + cancel)
│   │   └── BatchGenerationProgress/ # Batch SSE progress (N треков)
│   ├── services/
│   │   └── api.ts                 # Backend API client (fetch + cancelTrack + generateTrackBatch)
│   └── types/
│       └── index.ts               # TypeScript types (+ SSE event types)
├── tests/
│   └── e2e/                       # Playwright E2E tests
│       ├── profile-upload.spec.ts
│       ├── track-detail.spec.ts
│       └── generation-progress.spec.ts
├── Dockerfile
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.mjs

docs/                              # Algorithm specifications
├── algorithm_v1.md                # Full system (3 phases, 8 blocks)
├── phase_a.md                     # Phase A: profiling (v2)
└── phase_b.md                     # Phase B: course generation

specs/                             # Feature specs (SpecKit)
└── 001-algo-testing-mvp/
    ├── spec.md                    # This feature specification
    ├── plan.md                    # This implementation plan
    ├── research.md                # Phase 0 research (to be created)
    ├── data-model.md              # Phase 1 data model (to be created)
    ├── quickstart.md              # Phase 1 quickstart (to be created)
    ├── contracts/                 # Phase 1 API contracts (to be created)
    └── tasks.md                   # Phase 2 tasks (created by /speckit.tasks)

.specify/                          # SpecKit framework
├── memory/
│   └── constitution.md            # Project constitution (5 principles)
└── templates/                     # SpecKit templates

docker-compose.yml                 # Docker orchestration
.env.example                       # Environment variables template
CLAUDE.md                          # Project instructions for Claude Code
```

**Structure Decision**: Web application (Option 2) с дополнительным ML-сервисом. Три FastAPI приложения (backend, ml) + один Next.js frontend, изолированные в отдельных Docker-контейнерах и общающиеся через HTTP API. Структура соответствует Принципу I конституции (Container Isolation).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Нет нарушений конституции** — таблица не заполняется.
