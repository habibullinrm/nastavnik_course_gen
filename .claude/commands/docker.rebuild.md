---
description: Пересборка всех Docker контейнеров проекта
---

# Docker Rebuild

Полная пересборка Docker контейнеров с очисткой кеша.

## Outline

1. Остановка всех контейнеров
2. Пересборка образов без кеша
3. Запуск контейнеров в фоне
4. Проверка статуса
5. Просмотр логов

## Implementation

Выполнить последовательно:

```bash
# Остановка контейнеров
docker compose down

# Пересборка без кеша
docker compose build --no-cache

# Запуск в фоне
docker compose up -d

# Проверка статуса
docker compose ps

# Логи (последние 50 строк)
docker compose logs --tail=50
```

## Expected Output

Все 4 контейнера должны быть в статусе `running`:
- nastavnik_backend
- nastavnik_ml
- nastavnik_frontend
- nastavnik_db