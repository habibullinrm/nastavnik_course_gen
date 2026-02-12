# Quickstart: Сервис тестирования алгоритма генерации учебных треков

**Feature**: 001-algo-testing-mvp | **Date**: 2026-02-12

## Предварительные требования

- Docker и Docker Compose (v2.20+)
- Ключ DeepSeek API

## Быстрый запуск

### 1. Клонирование и настройка окружения

```bash
git clone <repo-url> && cd nastavnik_course_gen
git checkout 001-algo-testing-mvp

cp .env.example .env
# Отредактировать .env — заполнить DEEPSEEK_API_KEY
```

### 2. Запуск всех сервисов

```bash
docker compose up --build
```

Сервисы:
| Сервис | Порт | Описание |
|--------|------|----------|
| frontend | http://localhost:3000 | Next.js UI |
| backend | http://localhost:8000 | FastAPI — профили, треки, QA, экспорт |
| ml | http://localhost:8001 | FastAPI — pipeline B1-B8, CDV |
| db | localhost:5432 | PostgreSQL |

### 3. Проверка работоспособности

```bash
# Backend health
curl http://localhost:8000/api/health

# ML service health
curl http://localhost:8001/health
```

## Основные сценарии

### Загрузка профиля и генерация трека

```bash
# 1. Загрузить JSON-профиль
curl -X POST http://localhost:8000/api/profiles \
  -F "file=@sample_profile.json" \
  | jq .

# Ответ: { "id": "uuid-...", "valid": true, "errors": [], "warnings": [...] }

# 2. Запустить генерацию трека
curl -X POST http://localhost:8000/api/tracks/generate \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "uuid-..."}' \
  | jq .

# Ответ: { "track_id": "uuid-...", "status": "generating", "progress_url": "..." }

# 3. Получить результат (после завершения)
curl http://localhost:8000/api/tracks/{track_id} | jq .
```

### Пакетная генерация (QA)

```bash
# 1. Запустить пакетную генерацию (5 версий)
curl -X POST http://localhost:8000/api/qa/generate-batch \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "uuid-...", "batch_size": 5}' \
  | jq .

# 2. Получить QA-отчёт
curl http://localhost:8000/api/qa/reports/{report_id} | jq .
```

### Экспорт

```bash
# Экспорт трека
curl -o track.json http://localhost:8000/api/export/tracks/{track_id}

# Экспорт QA-отчёта
curl -o qa_report.json http://localhost:8000/api/export/qa-reports/{report_id}

# Экспорт всех версий + отчёт (ZIP)
curl -o qa_all.zip http://localhost:8000/api/export/qa-reports/{report_id}/all
```

## Пример JSON-профиля (минимальный)

```json
{
  "topic": "Элементы математической логики",
  "subject_area": "Математика",
  "experience_level": "beginner",
  "desired_outcomes": [
    "Решать задачи на таблицы истинности",
    "Строить отрицания с кванторами"
  ],
  "target_tasks": [
    {
      "id": "t1",
      "description": "Строить таблицы истинности для сложных формул",
      "complexity_rank": 1
    },
    {
      "id": "t2",
      "description": "Доказывать логические законы через таблицы",
      "complexity_rank": 2
    },
    {
      "id": "t3",
      "description": "Строить отрицания для высказываний с кванторами",
      "complexity_rank": 3
    }
  ],
  "task_hierarchy": [
    { "id": "t1", "description": "Строить таблицы истинности", "complexity_rank": 1 },
    { "id": "t2", "description": "Доказывать логические законы", "complexity_rank": 2 },
    { "id": "t3", "description": "Строить отрицания с кванторами", "complexity_rank": 3 }
  ],
  "peak_task_id": "t3",
  "easiest_task_id": "t1",
  "subtasks": [
    {
      "id": "st1",
      "description": "Определить структуру утверждения: где кванторы",
      "parent_task_id": "t3",
      "required_knowledge": ["кванторы"],
      "required_skills": ["анализ структуры"]
    },
    {
      "id": "st2",
      "description": "Применить правило: ¬∀ = ∃¬",
      "parent_task_id": "t3",
      "required_knowledge": ["правила отрицания кванторов"],
      "required_skills": ["подстановка"]
    }
  ],
  "confusing_concepts": [
    {
      "id": "c1",
      "term": "Импликация",
      "confusion_description": "Почему истинна при ложной посылке?"
    },
    {
      "id": "c2",
      "term": "Кванторы",
      "confusion_description": "Как читать ∀ и ∃?"
    }
  ],
  "diagnostic_result": "misconceptions",
  "weekly_hours": 5,
  "success_criteria": [
    {
      "id": "sc1",
      "description": "Решить ≥80% задач пробника",
      "measurable": true,
      "metric": "accuracy >= 0.8"
    }
  ]
}
```

## Структура переменных окружения (.env)

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# PostgreSQL
POSTGRES_USER=nastavnik
POSTGRES_PASSWORD=<your-password>
POSTGRES_DB=nastavnik_testing
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ML_SERVICE_URL=http://ml:8001

# ML Service
ML_HOST=0.0.0.0
ML_PORT=8001
DEEPSEEK_MAX_RETRIES=3
DEEPSEEK_RETRY_BACKOFF_BASE=2

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Разработка (без Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.main:app --reload --port 8000

# ML Service
cd ml
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8001

# Frontend
cd frontend
npm install
npm run dev

# Тесты
cd backend && pytest
cd ml && pytest
cd frontend && npm run test
```

## API-документация

После запуска:
- Backend Swagger: http://localhost:8000/docs
- ML Service Swagger: http://localhost:8001/docs