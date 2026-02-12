---
description: Проверка соответствия проекта 5 принципам конституции
---

# Validate Constitution

Полная проверка соблюдения принципов конституции проекта.

## Outline

1. Прочитать конституцию (.specify/memory/constitution.md)
2. Проверить каждый из 5 принципов
3. Вывести детальный отчёт

## Implementation

### Принцип I: Container Isolation

**Проверка:**
- ✅ Существует docker-compose.yml
- ✅ Существуют Dockerfile для backend, ml, frontend
- ✅ docker-compose.yml валиден (docker compose config)

```bash
# Проверка Docker конфигурации
bash .claude/hooks/scripts/docker-health-check.sh
```

### Принцип II: Explicit Dependencies

**Проверка:**
- ✅ backend/pyproject.toml содержит все зависимости
- ✅ ml/pyproject.toml содержит все зависимости
- ✅ frontend/package.json содержит все зависимости
- ✅ Нет импортов без объявления в зависимостях

```bash
# Проверка наличия файлов зависимостей
test -f backend/pyproject.toml && echo "✅ backend/pyproject.toml"
test -f ml/pyproject.toml && echo "✅ ml/pyproject.toml"
test -f frontend/package.json && echo "✅ frontend/package.json"
```

### Принцип III: Async-First Architecture

**Проверка:**
- ✅ Нет блокирующих вызовов (requests, time.sleep, open, sqlite3)
- ✅ Используются async библиотеки (httpx, aiofiles, asyncpg)
- ✅ FastAPI endpoints async def

```bash
# Поиск блокирующих вызовов
bash .claude/hooks/scripts/check-async-violations.sh backend/src/**/*.py ml/src/**/*.py
```

### Принцип IV: Russian Language

**Проверка:**
- ✅ Docstrings на русском языке
- ✅ Commit messages на русском
- ✅ Документация на русском (docs/*.md)

```bash
# Проверка docstrings
grep -r '"""' backend/src/ ml/src/ | grep -v '[А-Яа-яЁё]' || echo "✅ Docstrings на русском"

# Проверка последних коммитов
git log -5 --pretty=format:"%s" | grep -v '[А-Яа-яЁё]' && echo "⚠️ Найдены коммиты не на русском"
```

### Принцип V: Deepseek LLM Only

**Проверка:**
- ✅ ml/src/ использует только deepseek модели
- ✅ Нет импортов openai, anthropic (кроме тестов)

```bash
# Поиск не-deepseek LLM
grep -r 'openai\|anthropic\|gpt-\|claude-' ml/src/ || echo "✅ Только Deepseek LLM"
```

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️  ПРОВЕРКА КОНСТИТУЦИИ ПРОЕКТА
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Принцип I: Container Isolation
  ✅ docker-compose.yml существует и валиден
  ✅ Dockerfile для всех сервисов

Принцип II: Explicit Dependencies
  ✅ pyproject.toml для backend и ml
  ✅ package.json для frontend

Принцип III: Async-First Architecture
  ⚠️ Найдено 2 блокирующих вызова в backend/src/utils.py
  ✅ FastAPI endpoints используют async def

Принцип IV: Russian Language
  ✅ Docstrings на русском
  ⚠️ 1 коммит на английском языке

Принцип V: Deepseek LLM Only
  ✅ Только deepseek в ml/src/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ИТОГ: ✅ 4/5 принципов соблюдены полностью
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Notes

- Проверка не блокирует работу, только показывает отклонения
- ⚠️ Предупреждения не критичны, но требуют внимания
- ✅ Зелёные галочки - полное соответствие принципу