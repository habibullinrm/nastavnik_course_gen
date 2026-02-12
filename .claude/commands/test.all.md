---
description: Запуск всех тестов проекта (backend, ml, frontend)
---

# Test All

Последовательный запуск тестов для всех сервисов.

## Outline

1. Запуск pytest для backend
2. Запуск pytest для ml
3. Запуск npm test для frontend (если есть)

## Implementation

```bash
#!/usr/bin/env bash

set -e

ERRORS=0

# Backend тесты
if [ -d "backend/tests" ]; then
    echo "🧪 Запуск backend тестов..."
    cd backend

    if python -m pytest -xvs --tb=short; then
        echo "✅ Backend тесты пройдены"
    else
        echo "❌ Backend тесты не пройдены"
        ERRORS=$((ERRORS + 1))
    fi

    cd ..
else
    echo "⚠️ backend/tests/ не найдена"
fi

echo ""

# ML тесты
if [ -d "ml/tests" ]; then
    echo "🧪 Запуск ml тестов..."
    cd ml

    if python -m pytest -xvs --tb=short; then
        echo "✅ ML тесты пройдены"
    else
        echo "❌ ML тесты не пройдены"
        ERRORS=$((ERRORS + 1))
    fi

    cd ..
else
    echo "⚠️ ml/tests/ не найдена"
fi

echo ""

# Frontend тесты (опционально)
if [ -f "frontend/package.json" ]; then
    cd frontend

    # Проверяем наличие test скрипта
    if grep -q '"test"' package.json; then
        echo "🧪 Запуск frontend тестов..."

        if npm test; then
            echo "✅ Frontend тесты пройдены"
        else
            echo "❌ Frontend тесты не пройдены"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "⚠️ Frontend тесты не настроены (нет скрипта 'test')"
    fi

    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo "✅ Все тесты пройдены успешно"
    exit 0
else
    echo "❌ Обнаружено ошибок: $ERRORS"
    exit 1
fi
```

## Pytest Flags

- `-x` - остановка на первой ошибке
- `-v` - verbose режим
- `-s` - показывать print() вывод
- `--tb=short` - короткий traceback

## Notes

- Тесты запускаются последовательно (backend → ml → frontend)
- При ошибке в одном сервисе, остальные всё равно запустятся
- Финальный exit code: 0 если все OK, 1 если есть ошибки