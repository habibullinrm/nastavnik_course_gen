# Tasks: Сервис тестирования алгоритма генерации учебных треков

**Input**: Design documents from `/specs/001-algo-testing-mvp/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Добавлены ручные валидационные тесты после каждой фазы (T009a, T027a, T049a, T057a, T067a, T072a, T077b). Автоматические unit/integration тесты (pytest) не включены.

**Organization**: Задачи сгруппированы по user stories для независимой реализации и тестирования.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Можно запускать параллельно (разные файлы, нет зависимостей)
- **[Story]**: К какой user story относится задача (US1, US2, US3, US4)
- Пути указаны относительно корня репозитория

## Path Conventions

- **Backend**: `backend/src/`, `backend/alembic/`
- **ML-сервис**: `ml/src/`
- **Frontend**: `frontend/src/`
- **Корень**: `docker-compose.yml`, `.env.example`

---

## Phase 1: Setup (Инициализация проекта)

**Purpose**: Создание структуры проекта и инициализация зависимостей для всех 4 контейнеров

- [X] T001 Создать корневую структуру каталогов: `backend/`, `ml/`, `frontend/`, и файлы `docker-compose.yml`, `.env.example`
- [X] T002 [P] Инициализировать backend Python-проект: `backend/pyproject.toml` с зависимостями (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, httpx, alembic, python-multipart)
- [X] T003 [P] Инициализировать ML Python-проект: `ml/pyproject.toml` с зависимостями (fastapi, uvicorn, httpx, pydantic, sse-starlette)
- [X] T004 [P] Инициализировать frontend Next.js-проект: `frontend/package.json` с зависимостями (next, react, tailwindcss, typescript); настроить `frontend/tailwind.config.ts`, `frontend/tsconfig.json`, `frontend/next.config.ts`
- [X] T005 [P] Создать `backend/Dockerfile` (Python 3.11, uvicorn)
- [X] T006 [P] Создать `ml/Dockerfile` (Python 3.11, uvicorn)
- [X] T007 [P] Создать `frontend/Dockerfile` (Node 20, next build + start)
- [X] T008 Создать `docker-compose.yml` с 4 сервисами: frontend (:3000), backend (:8000), ml (:8001), db (PostgreSQL 16, :5432); volumes для db; internal network
- [X] T009 Создать `.env.example` с переменными: DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, POSTGRES_*, BACKEND_*, ML_*, NEXT_PUBLIC_API_URL (согласно quickstart.md)
- [X] T009a [TEST] Smoke test Phase 1: docker compose up, проверка healthcheck всех 4 сервисов (frontend :3000, backend :8000, ml :8001, db :5432), нет ошибок в логах

---

## Phase 2: Foundational (Блокирующие предпосылки)

**Purpose**: Инфраструктура, которая ДОЛЖНА быть готова до начала работы над user stories

**⚠️ CRITICAL**: Ни одна user story не может быть начата до завершения этой фазы

- [X] T010 Создать конфигурацию backend: `backend/src/core/config.py` — Pydantic Settings (DB URL, ML_SERVICE_URL, порты) с загрузкой из .env
- [X] T011 Создать async database engine: `backend/src/core/database.py` — AsyncEngine (asyncpg), async SessionLocal, Base declarative
- [X] T012 Создать главное приложение backend: `backend/src/main.py` — FastAPI app, lifespan (создание таблиц), подключение роутеров, CORS middleware
- [X] T013 [P] Создать SQLAlchemy-модель StudentProfile: `backend/src/models/student_profile.py` — таблица `student_profiles` (id UUID PK, data JSONB, filename, validation_result JSONB, topic, experience_level, created_at, updated_at) согласно data-model.md
- [X] T014 [P] Создать SQLAlchemy-модель PersonalizedTrack: `backend/src/models/personalized_track.py` — таблица `personalized_tracks` (id UUID PK, profile_id FK, qa_report_id FK nullable, track_data JSONB, generation_metadata JSONB, algorithm_version, validation_b8 JSONB, status, error_message, generation_duration_sec, batch_index, created_at, updated_at) согласно data-model.md
- [X] T015 [P] Создать SQLAlchemy-модель QAReport: `backend/src/models/qa_report.py` — таблица `qa_reports` (id UUID PK, profile_id FK, report_data JSONB, batch_size, completed_count, mean_cdv, cdv_std, recommendation, status, error_message, created_at, updated_at) согласно data-model.md
- [X] T016 Настроить Alembic: `backend/alembic.ini`, `backend/alembic/env.py` (async); создать начальную миграцию со всеми 4 таблицами (включая generation_logs) и индексами (GIN на JSONB, BTREE на FK и status)
- [X] T017 [P] Создать Pydantic-схемы валидации StudentProfile: `backend/src/schemas/student_profile.py` — StudentProfileInput (все поля из phase_a.md с CRITICAL/IMPORTANT/OPTIONAL разметкой), ValidationResult (valid, errors[], warnings[]), ProfileUploadResponse, ProfileSummary, ProfileDetail. **Примечание**: поле `diagnostic_result` (phase_a.md) = `diagnostic_level` (phase_b.md) — использовать имя `diagnostic_result` как каноническое, в B1 маппить на `diagnostic_level`
- [X] T018 [P] Создать Pydantic-схемы треков: `backend/src/schemas/track.py` — GenerationStartedResponse, TrackDetail, TrackSummary, TrackListResponse, FieldUsageResponse
- [X] T019 [P] Создать Pydantic-схемы QA: `backend/src/schemas/qa_report.py` — BatchStartedResponse, QAReportDetail, QAReportListResponse, CDVPair, TopicFrequency
- [X] T020 [P] Создать конфигурацию ML-сервиса: `ml/src/core/config.py` — Pydantic Settings (DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, MAX_RETRIES, RETRY_BACKOFF_BASE)
- [X] T021 [P] Создать DeepSeek async client с retry: `ml/src/services/deepseek_client.py` — httpx.AsyncClient, structured output (JSON), retry до 3 раз с exponential backoff, обработка 429/5xx/timeout/невалидный JSON, логирование вызовов и токенов
- [X] T022 Создать главное приложение ML-сервиса: `ml/src/main.py` — FastAPI app, подключение роутеров (/pipeline, /cdv, /health)
- [X] T023 [P] Создать Pydantic-схемы pipeline: `ml/src/schemas/pipeline.py` — PipelineRunRequest, PipelineRunResponse, GenerationMetadata, StepLog, PipelineError (согласно contracts/ml-api.yaml)
- [X] T024 [P] Создать Pydantic-схемы CDV: `ml/src/schemas/cdv.py` — CDVCalculateRequest, CDVCalculateResponse, CDVPair, TopicFrequency
- [X] T025 [P] Создать базовые TypeScript-типы: `frontend/src/types/index.ts` — StudentProfile, PersonalizedTrack, TrackSummary, QAReport, ValidationResult, GenerationProgress (типы совпадают с backend API-ответами)
- [X] T026 [P] Создать API-клиент frontend: `frontend/src/services/api.ts` — базовый fetch wrapper с обработкой ошибок, BASE_URL из env; функции: uploadProfile, generateTrack, getTrack, listTracks, и т.д.
- [X] T027 Создать layout frontend: `frontend/src/app/layout.tsx` — корневой layout с Tailwind CSS, навигация (Загрузка | Треки | QA | Профили)
- [X] T027a [TEST] Integration test Phase 2: Alembic миграции применены, таблицы созданы (student_profiles, personalized_tracks, qa_reports, generation_logs), Pydantic-схемы валидируют тестовый JSON, DeepSeek client доступен

**Checkpoint**: Фундамент готов — можно начинать реализацию user stories

---

## Phase 3: User Story 1 — Загрузка профиля и генерация трека (Priority: P1) 🎯 MVP

**Goal**: Разработчик загружает JSON-профиль, запускает pipeline B1-B8, получает `PersonalizedTrack`

**Independent Test**: Загрузить корректный JSON, нажать «Сгенерировать», увидеть полный PersonalizedTrack с компетенциями, ЗУН, расписанием

### Backend — загрузка и валидация профиля

- [X] T028 [US1] Реализовать сервис профилей: `backend/src/services/profile_service.py` — async функции: upload_and_validate (парсинг JSON, валидация через Pydantic, сохранение в БД, возврат errors/warnings), get_profile, list_profiles
- [X] T029 [US1] Реализовать роутер профилей: `backend/src/api/profiles.py` — POST /api/profiles (multipart upload, FR-001–FR-004), GET /api/profiles, GET /api/profiles/{id}; подключить в main.py

### ML — Промежуточные схемы и промпты

- [X] T030 [US1] Создать Pydantic-схемы промежуточных результатов B1-B8: `ml/src/schemas/pipeline_steps.py` — ValidatedStudentProfile (B1 output), CompetencySet (B2: competencies[], integral_competency_id, competency_task_map, competency_outcome_map), KSAMatrix (B3: knowledge_items[], skill_items[], habit_items[], dependency_graph[]), LearningUnit (B4: TheoryUnit|PracticeUnit|AutomationUnit), LearningUnitCluster (B4), TrackLevel (B5), LessonBlueprint (B6), TrackWeek/TrackDay (B7), ValidationResult (B8) — все типы согласно docs/phase_b.md
- [X] T031 [US1] Создать шаблоны промптов для DeepSeek: `ml/src/prompts/` — по одному файлу на шаг (b1_prompt.py ... b8_prompt.py); каждый промпт: инструкция + входные данные + формат выхода (Pydantic-схема из T030) + критерии качества + примеры
- [X] T031a [US1] Создать сервис логирования шагов pipeline: `ml/src/services/step_logger.py` — async функция log_step(track_id, step_name, step_output, llm_calls, duration) → POST в backend /api/logs/step; опционально дублирование в `ml/logs/{track_id}/step_{B1..B8}.json`

### ML — Pipeline B1-B8

**Примечание**: Шаги B1-B8 помечены [P] для параллельности _разработки_ (разные файлы). При _выполнении_ pipeline шаги строго последовательны: B1→B2→B3→B4→B5→B6→B7→B8. Каждый шаг использует промпт из T031 и возвращает Pydantic-модель из T030.

- [X] T032 [P] [US1] Реализовать шаг B1 — валидация и обогащение профиля: `ml/src/pipeline/b1_validate.py` — проверка CRITICAL-полей, определение effective_level (матрица experience_level × diagnostic_result), обогащение system_generated данных, расчёт временных параметров (согласно docs/phase_b.md шаг B1). **Примечание**: маппить `diagnostic_result` (имя из профиля) → `diagnostic_level` (имя в phase_b.md)
- [X] T033 [P] [US1] Реализовать шаг B2 — формулирование компетенций: `ml/src/pipeline/b2_competencies.py` — LLM-вызов: интегральная компетенция из peak_task, составные компетенции из task_hierarchy, валидация покрытия desired_outcomes, пропедевтика для beginners (согласно docs/phase_b.md шаг B2)
- [X] T034 [P] [US1] Реализовать шаг B3 — декомпозиция в матрицу ЗУН: `ml/src/pipeline/b3_ksa_matrix.py` — LLM-вызовы: генерация Знаний (из confusing_concepts, barriers, gaps), Умений (из subtasks), Навыков (из mastery_signals, success_criteria); построение dependency graph (согласно docs/phase_b.md шаг B3)
- [X] T035 [P] [US1] Реализовать шаг B4 — проектирование учебных единиц: `ml/src/pipeline/b4_learning_units.py` — LLM-вызовы: theory-единицы из Знаний, practice-единицы из Умений, automation-единицы из Навыков; связывание по 4C/ID в кластеры (согласно docs/phase_b.md шаг B4)
- [X] T036 [P] [US1] Реализовать шаг B5 — иерархия и уровни: `ml/src/pipeline/b5_hierarchy.py` — LLM-вызов: топологическая сортировка, назначение уровней (Базовый→Средний→Продвинутый→Интеграционный), расчёт временного бюджета, сжатие при нехватке времени (согласно docs/phase_b.md шаг B5)
- [X] T037 [P] [US1] Реализовать шаг B6 — проблемные формулировки: `ml/src/pipeline/b6_problem_formulations.py` — LLM-вызовы: для каждого кластера генерация ПП, ожидаемых гипотез, КИ-порций, заданий на ПМ, противоречий, заданий на синтез, вопросов рефлексии, правил FSM (согласно docs/phase_b.md шаг B6)
- [X] T038 [P] [US1] Реализовать шаг B7 — сборка расписания: `ml/src/pipeline/b7_schedule.py` — распределение единиц по неделям и дням, встраивание checkpoint'ов и механизмов поддержки (согласно docs/phase_b.md шаг B7)
- [X] T039 [P] [US1] Реализовать шаг B8 — валидация трека: `ml/src/pipeline/b8_validation.py` — 22 проверки (покрытие, порядок, время, согласованность с профилем, FSM-готовность); retry при critical failures до 3 итераций (согласно docs/phase_b.md шаг B8)
- [X] T040 [US1] Реализовать оркестратор pipeline: `ml/src/services/pipeline_orchestrator.py` — async функция run_pipeline(profile) → PersonalizedTrack; последовательный запуск B1→B8, **после каждого шага вызов step_logger.log_step()**, сбор metadata (timing, tokens), обработка ошибок на каждом шаге

### ML — API endpoints

- [X] T041 [US1] Реализовать роутер pipeline: `ml/src/api/pipeline.py` — POST /pipeline/run (синхронный запуск, возврат PersonalizedTrack), POST /pipeline/run-stream (SSE: прогресс по шагам B1-B8 + финальный результат)
- [X] T042 [P] [US1] Реализовать health endpoint ML: `ml/src/api/health.py` — GET /health (статус + проверка доступности DeepSeek API через ping)

### Backend — генерация трека

- [X] T043 [US1] Реализовать сервис треков: `backend/src/services/track_service.py` — async функции: generate_track (вызов ML /pipeline/run-stream через httpx, сохранение результата в БД, обновление статуса), get_track, list_tracks; обработка ошибок ML-сервиса
- [X] T044 [US1] Реализовать роутер треков: `backend/src/api/tracks.py` — POST /api/tracks/generate (запуск генерации, возврат track_id + progress_url), GET /api/tracks/{id}, GET /api/tracks/{id}/progress (SSE проксирование с ML), GET /api/tracks (список с фильтрами); подключить в main.py
- [X] T044a [US1] Создать SQLAlchemy-модель GenerationLog: `backend/src/models/generation_log.py` — таблица generation_logs (id, track_id FK, step_name, step_output JSONB, llm_calls JSONB[], step_duration_sec, error_message, created_at); BTREE index на (track_id, step_name)
- [X] T044b [US1] Создать роутер логирования: `backend/src/api/logs.py` — POST /api/logs/step (сохранение логов от ML), GET /api/logs/track/{track_id}, GET /api/logs/track/{track_id}/step/{step_name}; подключить в main.py
- [X] T045 [P] [US1] Реализовать health endpoint backend: `backend/src/api/health.py` — GET /api/health (статус БД + доступность ML-сервиса)

### Frontend — загрузка и генерация

- [X] T046 [US1] Создать компонент загрузки JSON: `frontend/src/components/ProfileUpload/ProfileUpload.tsx` — drag-and-drop / file input, отправка на POST /api/profiles, отображение validation результата (errors красным, warnings жёлтым), кнопка «Сгенерировать трек»
- [X] T047 [US1] Создать компонент прогресса генерации: `frontend/src/components/GenerationProgress/GenerationProgress.tsx` — подключение к SSE /api/tracks/{id}/progress, отображение текущего шага (B1...B8), прогресс-бар, лог шагов
- [X] T048 [US1] Создать страницу загрузки: `frontend/src/app/page.tsx` — главная страница с ProfileUpload; после успешной загрузки — кнопка генерации; при генерации — переход на страницу прогресса
- [X] T049 [US1] Создать страницу прогресса генерации: `frontend/src/app/tracks/generate/page.tsx` — GenerationProgress; после завершения — перенаправление на просмотр трека
- [X] T049a [TEST] E2E test Phase 3 (US1): Загрузить sample JSON из quickstart.md → запустить генерацию → проверить PersonalizedTrack (competencies, ksa_matrix, learning_units, schedule не пустые) → проверить БД (track + 8 generation_logs)

**Checkpoint**: User Story 1 полностью функциональна — можно загрузить JSON, запустить генерацию, увидеть результат

---

## Phase 4: User Story 2 — Просмотр результатов генерации (Priority: P2)

**Goal**: Разработчик просматривает сгенерированный трек в древовидной структуре с метаданными и индикаторами полей

**Independent Test**: После генерации открыть трек и увидеть дерево (компетенции→ЗУН→единицы→расписание), метаданные, индикаторы полей

### Backend

- [X] T050 [US2] Реализовать сервис индикаторов полей: `backend/src/services/field_usage_service.py` — async функция get_field_usage(track_id) → анализ track_data: какие поля StudentProfile были использованы на каких шагах B1-B8, какие не использованы
- [X] T051 [US2] Добавить endpoint индикаторов полей: `backend/src/api/tracks.py` — GET /api/tracks/{id}/field-usage (возврат FieldUsageResponse)

### Frontend

- [ ] T052 [US2] Создать компонент TreeView: `frontend/src/components/TreeView/TreeView.tsx` — рекурсивный компонент с раскрытием/свёрткой узлов; уровни: Компетенции → ЗУН (Знания/Умения/Навыки) → Учебные единицы → Уровни → Недели → Дни → Учебные действия; длительность на каждом уровне
- [ ] T053 [P] [US2] Создать компонент метаданных генерации: `frontend/src/components/TrackMetadata/TrackMetadata.tsx` — версия алгоритма, timestamp, длительность генерации, количество LLM-вызовов, использованные токены, входные параметры (topic, experience_level, desired_outcomes)
- [ ] T054 [P] [US2] Создать компонент индикаторов полей: `frontend/src/components/FieldUsage/FieldUsage.tsx` — таблица использованных полей (с указанием шагов) и неиспользованных полей; зелёный/серый цвет
- [ ] T055 [P] [US2] Создать компонент расписания: `frontend/src/components/WeeklySchedule/WeeklySchedule.tsx` — понедельное расписание: неделя → дни → учебные единицы с длительностями; checkpoint'ы выделены
- [ ] T056 [US2] Создать страницу просмотра трека: `frontend/src/app/tracks/[id]/page.tsx` — загрузка трека по ID, табы: «Дерево курса» (TreeView), «Расписание» (WeeklySchedule), «Метаданные» (TrackMetadata), «Поля профиля» (FieldUsage); результат валидации B8
- [X] T057 [P] [US2] Создать страницу списка треков: `frontend/src/app/tracks/page.tsx` — таблица треков (topic, статус, дата, длительность генерации); фильтр по профилю; клик → страница просмотра
- [ ] T057a [TEST] UI test Phase 4 (US2): Открыть трек → проверить TreeView (раскрытие компетенций→ЗУН→единиц), метаданные (версия алгоритма, LLM calls), field usage, WeeklySchedule

**Checkpoint**: User Stories 1 И 2 работают — можно загрузить, сгенерировать и детально просмотреть трек

---

## Phase 5: User Story 3 — Контроль качества: пакетная генерация и CDV (Priority: P3)

**Goal**: Разработчик запускает N генераций из одного профиля и видит QA-отчёт с CDV-метриками и рекомендацией по стабильности

**Independent Test**: Загрузить JSON, запустить 5 генераций, увидеть CDV-таблицу и рекомендацию «стабильный/нестабильный»

### ML — CDV Calculator

- [ ] T058 [US3] Реализовать CDV-калькулятор: `ml/src/services/cdv_calculator.py` — расчёт CDV между парами треков: Jaccard similarity по темам (вес 0.4), подтемам (вес 0.3), учебным действиям (вес 0.3); нормализация имён (lowercase, стеммирование); CDV = 1 - weighted_sim; агрегация: mean_cdv, cdv_std, top-5 stable/unstable, recommendation (stable < 0.15, needs_improvement 0.15-0.30, unstable > 0.30). **Примечание**: Маппинг на структуру PersonalizedTrack: "темы" = LearningUnit.title, "подтемы" = KSA items (knowledge/skill/habit titles), "учебные действия" = lesson activities (theory/practice/automation содержимое)
- [ ] T059 [US3] Реализовать роутер CDV: `ml/src/api/cdv.py` — POST /cdv/calculate (принимает массив треков, возвращает CDVCalculateResponse)

### Backend — пакетная генерация

- [ ] T060 [US3] Реализовать сервис QA: `backend/src/services/qa_service.py` — async функции: start_batch_generation (создание QAReport, последовательный запуск N pipeline через ML, обработка частичных сбоев — сохранение готовых версий, вызов CDV calculate, обновление QAReport), get_qa_report, list_qa_reports
- [ ] T061 [US3] Реализовать роутер QA: `backend/src/api/qa.py` — POST /api/qa/generate-batch (запуск batch, возврат report_id + progress_url), GET /api/qa/reports/{id}, GET /api/qa/reports/{id}/progress (SSE: номер текущей генерации, статус), GET /api/qa/reports (список); подключить в main.py

### Frontend — QA

- [ ] T062 [US3] Создать компонент запуска пакетной генерации: `frontend/src/components/BatchGeneration/BatchGeneration.tsx` — выбор профиля, ввод количества (1-100), кнопка «Запустить»; подключение к SSE прогресса (текущая генерация X из N)
- [ ] T063 [P] [US3] Создать компонент CDV-таблицы: `frontend/src/components/QAReport/CDVMatrix.tsx` — сводная таблица CDV по парам версий; цветовая кодировка (зелёный < 15%, жёлтый 15-30%, красный > 30%)
- [ ] T064 [P] [US3] Создать компонент стабильности тем: `frontend/src/components/QAReport/TopicStability.tsx` — частота тем (N из M версий), топ-5 стабильных, топ-5 нестабильных
- [ ] T065 [P] [US3] Создать компонент рекомендации: `frontend/src/components/QAReport/Recommendation.tsx` — итоговые индикаторы: средний CDV, стандартное отклонение, рекомендация (стабильный / требует доработки / нестабильный) с цветовой индикацией
- [ ] T066 [US3] Создать страницу запуска QA: `frontend/src/app/qa/page.tsx` — BatchGeneration + список предыдущих QA-отчётов
- [ ] T067 [US3] Создать страницу QA-отчёта: `frontend/src/app/qa/[id]/page.tsx` — загрузка отчёта по ID; CDVMatrix + TopicStability + Recommendation; ссылки на отдельные версии треков
- [ ] T067a [TEST] Batch test Phase 5 (US3): Запустить batch N=5 → проверить 5 треков, CDV-матрицу 5×5, mean_cdv, recommendation → проверить частичный сбой (N=3, прервать на 2-й)

**Checkpoint**: User Stories 1, 2 И 3 работают — полный цикл: загрузка → генерация → просмотр → пакетное сравнение

---

## Phase 6: User Story 4 — Экспорт результатов (Priority: P4)

**Goal**: Разработчик экспортирует трек или QA-отчёт в JSON/ZIP для offline-анализа

**Independent Test**: Сгенерировать трек, нажать «Экспорт», скачать JSON-файл с полной структурой PersonalizedTrack

### Backend

- [ ] T068 [US4] Реализовать сервис экспорта: `backend/src/services/export_service.py` — async функции: export_track (формирование JSON с именем track_[topic]_[timestamp].json), export_qa_report (JSON отчёта), export_qa_all (ZIP: все версии + отчёт через zipfile в StreamingResponse)
- [ ] T069 [US4] Реализовать роутер экспорта: `backend/src/api/export.py` — GET /api/export/tracks/{id}, GET /api/export/qa-reports/{id}, GET /api/export/qa-reports/{id}/all (ZIP); Content-Disposition: attachment; подключить в main.py

### Frontend

- [ ] T070 [P] [US4] Создать компонент кнопки экспорта: `frontend/src/components/ExportButton/ExportButton.tsx` — универсальная кнопка экспорта (принимает URL, filename); инициирует скачивание через fetch + Blob
- [ ] T071 [US4] Интегрировать ExportButton в страницу трека: `frontend/src/app/tracks/[id]/page.tsx` — кнопка «Экспорт JSON» на странице просмотра трека
- [ ] T072 [US4] Интегрировать ExportButton в страницу QA-отчёта: `frontend/src/app/qa/[id]/page.tsx` — кнопки «Экспорт отчёта» и «Экспорт всех версий (ZIP)»
- [ ] T072a [TEST] Export test Phase 6 (US4): Экспорт трека (JSON валидный), экспорт QA-отчёта, экспорт ZIP всех версий → проверить содержимое файлов

**Checkpoint**: Все 4 user stories полностью функциональны

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Финализация, качество кода, кросс-сервисные улучшения

- [ ] T073 Финализировать docker-compose.yml: healthcheck для всех сервисов, depends_on с condition: service_healthy, restart policy, volume для PostgreSQL данных
- [ ] T074 [P] Создать страницу списка профилей: `frontend/src/app/profiles/[id]/page.tsx` — просмотр загруженного профиля (форматированный JSON), список связанных треков и QA-отчётов
- [ ] T075 [P] Добавить обработку edge cases в backend: ошибки парсинга JSON (позиция ошибки), LLM невалидный ответ (retry + информативное сообщение), превышение лимита токенов, прерывание batch на i-м запуске (частичный отчёт), B8 critical failures
- [ ] T076 [P] Добавить обработку edge cases в frontend: loading states, error boundaries, пустые состояния (нет треков/отчётов), отображение частичных QA-отчётов
- [ ] T077 Валидация quickstart.md: проверить docker compose up, выполнить все curl-примеры из quickstart.md, убедиться в корректности
- [ ] T077a [P] Создать страницу debug-логов: `frontend/src/app/tracks/[id]/debug/page.tsx` — отображение всех шагов B1-B8 для трека, раскрываемые блоки с JSON-выводом, подсветка LLM-вызовов (prompt, response, токены)
- [ ] T077b [TEST] Regression test Phase 7: Повторить тесты Phase 3–6 на новом профиле, проверить edge cases (T075-T076), все примеры из quickstart.md, healthcheck всех сервисов

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Нет зависимостей — можно начинать сразу
- **Foundational (Phase 2)**: Зависит от Setup — БЛОКИРУЕТ все user stories
- **User Stories (Phase 3–6)**: Все зависят от Foundational
  - US1 (P1): можно начинать сразу после Phase 2
  - US2 (P2): зависит от US1 (нужны сгенерированные треки для просмотра)
  - US3 (P3): зависит от US1 (нужен pipeline для пакетной генерации)
  - US4 (P4): зависит от US1 (экспорт треков); частично от US3 (экспорт QA-отчётов)
- **Polish (Phase 7)**: Зависит от всех желаемых user stories

### User Story Dependencies

```
Phase 1: Setup
    │
Phase 2: Foundational
    │
    ├── Phase 3: US1 — Загрузка + Генерация (P1) 🎯 MVP
    │       │
    │       ├── Phase 4: US2 — Просмотр результатов (P2)
    │       │
    │       ├── Phase 5: US3 — Пакетная генерация + CDV (P3)
    │       │       │
    │       │       └── Phase 6: US4 — Экспорт (P4) [частично]
    │       │
    │       └── Phase 6: US4 — Экспорт (P4) [трек]
    │
Phase 7: Polish
```

### Within Each User Story

- Модели → сервисы → эндпоинты → frontend
- ML-компоненты можно делать параллельно с backend (разные сервисы)
- Frontend зависит от готовых API-эндпоинтов

### Parallel Opportunities

**Phase 1:**
- T002, T003, T004 (инициализация 3 проектов) — параллельно
- T005, T006, T007 (3 Dockerfile) — параллельно

**Phase 2:**
- T013, T014, T015 (3 SQLAlchemy-модели) — параллельно
- T017, T018, T019 (Pydantic-схемы backend) — параллельно
- T020, T021, T023, T024 (ML конфиг + клиент + схемы) — параллельно
- T025, T026 (frontend типы + API-клиент) — параллельно

**Phase 3 (US1):**
- T030 (Pydantic-схемы промежуточных B1-B8), T031 (prompt templates) — последовательно (T031 зависит от T030)
- T032–T039 (шаги B1-B8) — параллельно (разные файлы, нет зависимостей между ними; оркестратор T040 собирает их)
- T046, T047 (frontend компоненты) — параллельно

**Phase 4 (US2):**
- T052, T053, T054, T055 (frontend компоненты) — параллельно

**Phase 5 (US3):**
- T063, T064, T065 (frontend компоненты QA-отчёта) — параллельно

---

## Parallel Example: User Story 1

```bash
# Сначала создать схемы и промпты (последовательно):
Task: T030 "Pydantic-схемы промежуточных B1-B8 в ml/src/schemas/pipeline_steps.py"
Task: T031 "Промпты для DeepSeek в ml/src/prompts/"

# Затем ML pipeline шаги — все параллельно (разные файлы):
Task: T032 "Шаг B1 — валидация профиля в ml/src/pipeline/b1_validate.py"
Task: T033 "Шаг B2 — компетенции в ml/src/pipeline/b2_competencies.py"
Task: T034 "Шаг B3 — матрица ЗУН в ml/src/pipeline/b3_ksa_matrix.py"
Task: T035 "Шаг B4 — учебные единицы в ml/src/pipeline/b4_learning_units.py"
Task: T036 "Шаг B5 — иерархия в ml/src/pipeline/b5_hierarchy.py"
Task: T037 "Шаг B6 — проблемные формулировки в ml/src/pipeline/b6_problem_formulations.py"
Task: T038 "Шаг B7 — расписание в ml/src/pipeline/b7_schedule.py"
Task: T039 "Шаг B8 — валидация в ml/src/pipeline/b8_validation.py"

# После завершения всех шагов:
Task: T040 "Оркестратор pipeline в ml/src/services/pipeline_orchestrator.py"
```

## Parallel Example: User Story 2

```bash
# Frontend компоненты — все параллельно:
Task: T052 "TreeView в frontend/src/components/TreeView/TreeView.tsx"
Task: T053 "TrackMetadata в frontend/src/components/TrackMetadata/TrackMetadata.tsx"
Task: T054 "FieldUsage в frontend/src/components/FieldUsage/FieldUsage.tsx"
Task: T055 "WeeklySchedule в frontend/src/components/WeeklySchedule/WeeklySchedule.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T009)
2. Complete Phase 2: Foundational (T010–T027)
3. Complete Phase 3: User Story 1 (T028–T049)
4. **STOP and VALIDATE**: Загрузить JSON, запустить pipeline, получить PersonalizedTrack
5. Deploy/demo если готово

### Incremental Delivery

1. Setup + Foundational → Фундамент готов
2. Add US1 → Загрузка + генерация → Deploy (MVP!)
3. Add US2 → Просмотр дерева курса → Deploy
4. Add US3 → Пакетная генерация + CDV → Deploy
5. Add US4 → Экспорт → Deploy
6. Polish → Финализация

### Suggested MVP Scope

**Рекомендация**: MVP = Phase 1 + Phase 2 + Phase 3 (US1) + тесты
- 54 задачи (T001–T049a)
- Включает логирование для отладки (generation_logs)
- Покрывает ядро сервиса: загрузка профиля → pipeline B1-B8 → PersonalizedTrack → debug-логи
- Позволяет немедленно начать тестирование алгоритма с полной трассировкой шагов

---

## Notes

- [P] tasks = разные файлы, нет зависимостей
- [Story] label связывает задачу с user story
- [TEST] tasks = ручные валидационные тесты после каждой фазы
- Коммит после каждой задачи или логической группы
- Каждый checkpoint — точка для валидации
- Документация и коммиты на русском (Принцип IV конституции)
- Все эндпоинты — async def (Принцип III)
- DeepSeek API — единственный LLM-провайдер (Принцип V)