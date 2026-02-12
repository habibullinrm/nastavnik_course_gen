---
description: Обновление CLAUDE.md из plan.md и других источников
---

# Sync Context

Синхронизация контекста Claude из plan.md (SpecKit workflow).

## Outline

1. Запустить update-agent-context.sh для claude
2. Показать diff CLAUDE.md
3. Показать обновлённые секции

## Implementation

```bash
#!/usr/bin/env bash

set -e

echo "🔄 Синхронизация контекста Claude..."
echo ""

# Проверка наличия скрипта
SCRIPT_PATH=".specify/scripts/bash/update-agent-context.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Скрипт $SCRIPT_PATH не найден"
    echo "   SpecKit framework не настроен?"
    exit 1
fi

# Создаём backup CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    cp CLAUDE.md CLAUDE.md.backup
    echo "📦 Создан backup: CLAUDE.md.backup"
fi

# Запускаем синхронизацию
echo "🔧 Запуск update-agent-context.sh..."
bash "$SCRIPT_PATH" claude

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Изменения в CLAUDE.md:"
echo ""

# Показываем diff
if git diff --no-index --color CLAUDE.md.backup CLAUDE.md 2>/dev/null; then
    echo "⚠️ Нет изменений в CLAUDE.md"
else
    echo ""
    echo "✅ CLAUDE.md обновлён"
fi

# Удаляем backup если изменений нет
if diff -q CLAUDE.md.backup CLAUDE.md >/dev/null 2>&1; then
    rm CLAUDE.md.backup
    echo ""
    echo "Файл CLAUDE.md уже актуален"
else
    echo ""
    echo "📝 Backup сохранён: CLAUDE.md.backup"
    echo "   Для просмотра: diff CLAUDE.md.backup CLAUDE.md"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## What Gets Updated

Скрипт `update-agent-context.sh` синхронизирует следующие секции в CLAUDE.md:

- **Active Technologies** - из plan.md
- **Recent Changes** - из plan.md
- **Branch Context** - из текущей ветки git
- **Repository Structure** - из файловой системы

## When to Use

Запускайте после:
- Создания нового feature spec (SpecKit workflow)
- Добавления новых зависимостей
- Изменения архитектуры проекта
- Создания новой ветки с feature

## Notes

- Автоматически создаёт backup (CLAUDE.md.backup)
- Показывает diff для review
- Безопасно запускать многократно
- Не перезаписывает ручные изменения в CLAUDE.md (только обновляет секции)