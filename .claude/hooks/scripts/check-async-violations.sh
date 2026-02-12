#!/usr/bin/env bash
# check-async-violations.sh - Проверка блокирующих вызовов (async-first нарушения)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Использование: $0 <файлы...>"
    exit 1
fi

FILES=("$@")
VIOLATIONS=0

# Паттерны для поиска блокирующих вызовов
PATTERNS=(
    "requests\."
    "time\.sleep"
    "\bopen\("
    "sqlite3\."
)

ALTERNATIVES=(
    "httpx (async HTTP клиент)"
    "asyncio.sleep (асинхронная задержка)"
    "aiofiles (асинхронная работа с файлами)"
    "asyncpg/aiosqlite (асинхронные БД драйверы)"
)

log_info "Проверка async-first нарушений (блокирующие вызовы)..."

for file in "${FILES[@]}"; do
    # Пропускаем не-Python файлы
    if [[ ! "$file" =~ \.py$ ]]; then
        continue
    fi

    # Пропускаем тесты (там допустимы синхронные вызовы)
    if [[ "$file" =~ /tests/ ]] || [[ "$file" =~ _test\.py$ ]] || [[ "$file" =~ test_.*\.py$ ]]; then
        continue
    fi

    for i in "${!PATTERNS[@]}"; do
        pattern="${PATTERNS[$i]}"
        alternative="${ALTERNATIVES[$i]}"

        if grep -n -E "$pattern" "$file" >/dev/null 2>&1; then
            log_warning "Файл $file содержит блокирующий вызов: $pattern"
            echo "  Альтернатива: $alternative"
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    done
done

# Если нарушения найдены, спросить пользователя
if [ $VIOLATIONS -gt 0 ]; then
    echo ""
    log_warning "Найдено $VIOLATIONS async-first нарушений (Принцип III конституции)"
    echo ""
    echo "Блокирующие вызовы замедляют систему и нарушают async-first архитектуру."
    echo "Рекомендуется использовать асинхронные альтернативы."
    echo ""
    read -p "Продолжить коммит? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Коммит отменён пользователем"
        exit 1
    fi

    log_info "Продолжение коммита (нарушения проигнорированы)"
fi

exit 0