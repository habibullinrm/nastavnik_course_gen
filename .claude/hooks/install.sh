#!/usr/bin/env bash
# install.sh - Установщик git hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_ROOT=$(git rev-parse --show-toplevel)
GIT_HOOKS_DIR="$GIT_ROOT/.git/hooks"

echo "🔧 Установка git hooks для nastavnik_course_gen..."
echo ""

# Проверка существования .git/hooks/
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "❌ Директория $GIT_HOOKS_DIR не найдена"
    echo "   Убедитесь, что вы находитесь в git репозитории"
    exit 1
fi

# Делаем все скрипты исполняемыми
echo "📝 Установка прав на исполнение для скриптов..."
chmod +x "$SCRIPT_DIR/pre-commit"
chmod +x "$SCRIPT_DIR/commit-msg"
chmod +x "$SCRIPT_DIR/pre-push"
chmod +x "$SCRIPT_DIR/scripts"/*.sh

# Копируем хуки в .git/hooks/
echo "📦 Копирование хуков в .git/hooks/..."

HOOKS=("pre-commit" "commit-msg" "pre-push")

for hook in "${HOOKS[@]}"; do
    SOURCE="$SCRIPT_DIR/$hook"
    TARGET="$GIT_HOOKS_DIR/$hook"

    if [ -f "$TARGET" ]; then
        echo "⚠️  Хук $hook уже существует, создаём backup: $hook.backup"
        cp "$TARGET" "$TARGET.backup"
    fi

    cp "$SOURCE" "$TARGET"
    chmod +x "$TARGET"
    echo "✅ Установлен: $hook"
done

echo ""
echo "🎉 Git hooks успешно установлены!"
echo ""
echo "Установленные хуки:"
echo "  • pre-commit  - валидация Python, TypeScript, async-first проверка"
echo "  • commit-msg  - проверка русского языка в коммитах"
echo "  • pre-push    - запуск тестов и проверка Docker конфигурации"
echo ""
echo "Для отключения хуков используйте: git commit --no-verify / git push --no-verify"
echo "Для просмотра документации: cat .claude/hooks/README.md"
echo ""