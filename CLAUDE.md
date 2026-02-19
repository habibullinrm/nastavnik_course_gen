# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**nastavnik_course_gen** — algorithm for generating personalized educational course tracks based on learner profiles. Currently in the specification/design phase with no production code yet.

Документация, спецификации, тз должны быть написаны на **Русском**.

## Repository Structure

- `docs/` — core algorithm specifications (~3500 lines):
  - `algorithm_v1.md` — full system architecture (3 phases, 8 blocks, ~35 steps)
  - `phase_a.md` — Phase A: interactive data collection & student profiling (v2, handles beginners)
  - `phase_b.md` — Phase B: LLM-driven course design & generation
- `.specify/` — SpecKit framework (templates, scripts, constitution)
- `.claude/commands/` — SpecKit CLI commands for structured development

## Algorithm Architecture

Three-phase system:
- **Phase A** — Student profiling (interactive, user-facing)
- **Phase B** — Course generation (automated by LLM, no user interaction)
- **Phase C** — Adaptive lesson delivery (problem-based)

Learning models used: 4C/ID, Problem-Based Learning (PBL), KZU framework (Knowledge → Skills → Practice).

### Criticality Levels (used in specs)

- 🔴 CRITICAL — required for core functionality
- 🟡 IMPORTANT — improves personalization quality
- 🟢 OPTIONAL — nice-to-have enhancements

Each specification step includes standard and fallback (novice-mode) scenarios.

## Development Workflow (SpecKit)

Feature development follows: **Branch → Spec → Plan → Tasks → Implement**

Branch naming: `[###]-[feature-name]` (e.g., `001-user-auth`)

Available SpecKit commands (invoke via `/speckit.<command>`):
- `specify` — create feature spec from natural language
- `clarify` — identify underspecified areas in a spec
- `plan` — generate implementation design artifacts
- `tasks` — break specs into dependency-ordered tasks
- `implement` — execute tasks from tasks.md
- `analyze` — cross-artifact consistency check
- `checklist` — generate quality checklist
- `constitution` — manage project principles
- `taskstoissues` — convert tasks to GitHub issues

## Git Hooks

Проект использует нативные git hooks для автоматической валидации качества кода:

**Установка:**
```bash
bash .claude/hooks/install.sh
```

**Хуки:**
- **pre-commit** — валидация Python (black, ruff), TypeScript (eslint, tsc), async-first проверка, SpecKit структура
- **commit-msg** — проверка русского языка в commit messages (Принцип IV конституции)
- **pre-push** — запуск pytest для backend/ml, проверка Docker конфигурации

**Отключение (не рекомендуется):**
```bash
git commit --no-verify
git push --no-verify
```

**Документация:** `.claude/hooks/README.md`

## Claude Skills

Доступные команды для быстрых операций:

**Docker:**
- `/docker.rebuild` — пересборка всех контейнеров с очисткой кеша
- `/docker.logs [service]` — просмотр логов (backend|ml|frontend|db)

**Тестирование:**
- `/test.all` — запуск всех тестов (backend + ml + frontend)
- `/test.backend [pattern]` — pytest для backend с фильтрацией
- `/test.ml [pattern]` — pytest для ml с фильтрацией

**Валидация и линтинг:**
- `/validate.constitution` — проверка соблюдения 5 принципов конституции
- `/lint.fix` — автоисправление ошибок форматирования (black, ruff, eslint)

**Синхронизация:**
- `/sync.context` — обновление CLAUDE.md из plan.md (SpecKit)

## Active Technologies
- Python 3.11+ (backend, ML), TypeScript/Next.js (frontend) + FastAPI, Next.js 14+, Tailwind CSS, httpx (async HTTP), Pydantic v2, SQLAlchemy 2.0 (async), alembic (001-algo-testing-mvp)
- PostgreSQL 16 (asyncpg) (001-algo-testing-mvp)
- TypeScript (Next.js 14), Python 3.11 + FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Tailwind CSS (003-manual-profile)
- PostgreSQL (JSONB), без файлового хранилища (003-manual-profile)
- Python 3.11+ (backend), TypeScript 5 (frontend) + FastAPI, SQLAlchemy 2.0 async (backend); Next.js 14+, Tailwind CSS (frontend) (004-track-inners)
- PostgreSQL 16 (asyncpg) — JSONB для track_data (без изменений схемы БД) (004-track-inners)

## Recent Changes
- 001-algo-testing-mvp: Added Python 3.11+ (backend, ML), TypeScript/Next.js (frontend) + FastAPI, Next.js 14+, Tailwind CSS, httpx (async HTTP), Pydantic v2, SQLAlchemy 2.0 (async), alembic
