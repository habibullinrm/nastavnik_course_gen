<!--
  Sync Impact Report
  ==================
  Version change: 0.0.0 (unfilled template) -> 1.0.0
  Modified principles: N/A (initial creation)
  Added sections:
    - Core Principles (5 principles from user input)
    - Architecture Constraints (inferred from docs/)
    - Quality & Development Standards (inferred from SpecKit + docs/)
    - Governance
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md — ✅ no update needed
      (Constitution Check section is generic; filled per feature)
    - .specify/templates/spec-template.md — ✅ no update needed
      (mandatory sections align with principles)
    - .specify/templates/tasks-template.md — ✅ no update needed
      (task structure is principle-agnostic)
    - .specify/templates/agent-file-template.md — ✅ no update needed
    - CLAUDE.md — ✅ no update needed (already aligned)
    - README.md — ✅ no update needed (minimal)
  Follow-up TODOs: None
-->

# nastavnik_course_gen Constitution

## Core Principles

### I. Container Isolation

Frontend, база данных, бэкенд и ML-сервисы MUST запускаться
в отдельных Docker-контейнерах. Каждый сервис:

- Имеет собственный `Dockerfile` и определён в `docker-compose.yml`.
- Взаимодействует с другими сервисами исключительно через сеть
  (HTTP/gRPC), а не через общую файловую систему или память.
- Может быть собран, запущен и остановлен независимо от остальных.

Контейнеры: `frontend`, `backend`, `ml`, `db`.

### II. Technology Stack

Стек технологий фиксирован и НЕ подлежит замене без
amendment конституции:

- **Frontend**: Next.js + Tailwind CSS.
- **Backend**: Python + FastAPI.
- **ML-сервис**: Python + FastAPI.
- **База данных**: PostgreSQL.
- **Оркестрация**: Docker Compose.

Добавление новых runtime-зависимостей (фреймворки, ORM, брокеры
сообщений) MUST быть обосновано и отражено в конституции.

### III. Async-First

Все HTTP-запросы между сервисами и все операции ввода-вывода
MUST быть асинхронными:

- Backend и ML-сервисы MUST использовать `async def` эндпоинты
  в FastAPI.
- Запросы к базе данных MUST выполняться через асинхронный
  драйвер (например, `asyncpg`).
- Запросы к внешним API (DeepSeek, прочие) MUST использовать
  асинхронный HTTP-клиент (например, `httpx.AsyncClient`).
- Frontend MUST выполнять API-вызовы неблокирующим способом.

Синхронные блокирующие вызовы в production-коде запрещены.

### IV. Russian Documentation (Google Docstring)

Вся документация проекта MUST быть на русском языке:

- Docstring-и в Python-коде MUST следовать формату
  Google Docstring на русском языке.
- Commit-сообщения MUST быть на русском.
- Спецификации в `docs/` и `specs/` MUST быть на русском.
- JSDoc/комментарии во frontend-коде MUST быть на русском.
- Имена переменных и функций остаются на английском.

### V. DeepSeek as LLM Provider

Для всех запросов к LLM (генерация курса, классификация
ответов, проведение уроков) система MUST использовать
DeepSeek API:

- ML-сервис MUST отправлять запросы к DeepSeek API.
- Промпты MUST следовать принципу структурированного
  промптинга: инструкция шага, входные данные, формат
  выхода (TypeScript-интерфейс), критерии качества, примеры.
- Ключи API MUST храниться в переменных окружения,
  а не в коде.
- Система MUST поддерживать graceful degradation при
  недоступности API (retry с backoff, информативные ошибки).

## Architecture Constraints

Система реализует трёхфазный pipeline для генерации
персонализированных учебных треков:

- **Фаза A** (Сбор данных): интерактивный диалог с
  пользователем через frontend → backend. Результат:
  `StudentProfile`.
- **Фаза B** (Проектирование курса): автоматический
  pipeline в ML-сервисе (шаги B1-B8) через DeepSeek.
  Результат: `PersonalizedTrack`.
- **Фаза C** (Проведение обучения): FSM-движок с 8
  состояниями (ПП, ГП, КИ, ПМ, ПТ, СЗ, РФ, ПЗ)
  в ML-сервисе. Интерактивный режим.

Ограничения:

- Фазы MUST выполняться последовательно: A → B → C.
- Данные передаются только вперёд: B получает
  `StudentProfile` из A; C получает `PersonalizedTrack` из B.
- Шаги фазы B (B1-B8) MUST выполняться в порядке
  зависимостей.
- Валидация трека (B8) — обязательный гейт перед фазой C.
- FSM фазы C MUST реализовывать полную таблицу переходов
  из Приложения A (`algorithm_v1.md`).
- Каждый шаг взаимодействия MUST предоставлять fallback-
  сценарий для новичков (Principle III из `phase_a.md`).

## Quality & Development Standards

### Педагогические модели

Генерация курса MUST основываться на:

- **4C/ID** — каркас проектирования учебных единиц.
- **PBL** — каждая тема начинается с практической проблемы.
- **ЗУН** — компетенции декомпозируются на Знания → Умения →
  Навыки.

### Покрытие

В каждом сгенерированном треке MUST выполняться:

- Каждый `desired_outcome` покрыт хотя бы одной компетенцией.
- Каждая компетенция имеет минимум 1 Знание, 1 Умение, 1 Навык.
- Каждый элемент ЗУН покрыт учебной единицей.
- Каждая учебная единица включена в расписание.
- Каждый `success_criterion` покрыт checkpoint-ом.

### Workflow разработки

Разработка фич следует pipeline SpecKit:
**Branch → Spec → Plan → Tasks → Implement**.

Именование веток: `[###]-[feature-name]`
(например, `001-data-collector`).

## Governance

Конституция является авторитетным источником принципов
проекта. Она превалирует над ad-hoc решениями.

**Процедура изменений**:

1. Предложить изменение с обоснованием.
2. Обновить этот файл.
3. Проверить согласованность с шаблонами и CLAUDE.md.
4. Коммит в формате:
   `docs: amend constitution to vX.Y.Z (<описание>)`.

**Версионирование** (Semantic Versioning):

- **MAJOR**: удаление или несовместимое изменение принципа.
- **MINOR**: новый принцип или существенное расширение.
- **PATCH**: уточнения формулировок, исправление опечаток.

**Compliance**: все PR и ревью спецификаций MUST проверять
соответствие принципам конституции. Для runtime-гайдлайнов
использовать `CLAUDE.md`.

**Version**: 1.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-12