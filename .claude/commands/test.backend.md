---
description: Запуск pytest тестов для backend сервиса
---

# Test Backend

Запуск тестов backend с поддержкой фильтрации.

## Arguments

`$ARGUMENTS` - паттерн для фильтрации тестов (опционально)

## Outline

1. Перейти в директорию backend/
2. Запустить pytest с заданными параметрами
3. Показать результаты

## Implementation

```bash
#!/usr/bin/env bash

set -e

if [ ! -d "backend/tests" ]; then
    echo "❌ Директория backend/tests/ не найдена"
    exit 1
fi

cd backend

echo "🧪 Запуск backend тестов..."
echo ""

# Проверка аргументов для фильтрации
if [ -n "$ARGUMENTS" ]; then
    echo "📌 Фильтр: $ARGUMENTS"
    python -m pytest -xvs --tb=short -k "$ARGUMENTS"
else
    python -m pytest -xvs --tb=short
fi
```

## Usage Examples

```bash
# Все тесты
/test.backend

# Только тесты с "profile" в названии
/test.backend profile

# Только тесты с "validation"
/test.backend validation
```

## Pytest Flags

- `-x` - остановка на первой ошибке
- `-v` - verbose режим
- `-s` - показывать print() вывод
- `--tb=short` - короткий traceback
- `-k PATTERN` - фильтрация по имени теста

## Notes

- Тесты запускаются в виртуальном окружении backend
- Для запуска конкретного файла: `/test.backend test_profiles.py`
- Для запуска конкретного теста: `/test.backend test_create_profile`