---
description: Просмотр логов Docker контейнеров
---

# Docker Logs

Просмотр логов контейнеров с автообновлением.

## Arguments

`$ARGUMENTS` - имя сервиса (backend | ml | frontend | db)

## Outline

1. Определить сервис из аргументов
2. Запустить `docker compose logs --tail=100 --follow [service]`

## Implementation

```bash
# Парсинг аргументов
SERVICE="${ARGUMENTS:-backend}"

# Проверка валидного сервиса
case "$SERVICE" in
    backend|ml|frontend|db)
        echo "📋 Логи сервиса: $SERVICE"
        docker compose logs --tail=100 --follow "$SERVICE"
        ;;
    *)
        echo "❌ Неизвестный сервис: $SERVICE"
        echo "Доступные: backend, ml, frontend, db"
        exit 1
        ;;
esac
```

## Usage Examples

```
/docker.logs backend
/docker.logs ml
/docker.logs db
/docker.logs          # по умолчанию backend
```

## Notes

- `--tail=100` показывает последние 100 строк
- `--follow` автоматически обновляет логи (Ctrl+C для выхода)