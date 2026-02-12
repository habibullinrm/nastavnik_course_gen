#!/usr/bin/env bash
# validate-python.sh - Валидация Python кода (black, ruff)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Использование: $0 <файлы...>"
    exit 1
fi

FILES=("$@")
ERRORS=0

# Проверка наличия инструментов
if ! command_exists black; then
    log_warning "black не установлен, пропускаем проверку форматирования"
else
    log_info "Проверка форматирования Python (black)..."

    for file in "${FILES[@]}"; do
        # Определяем директорию (backend или ml)
        if [[ "$file" == backend/* ]]; then
            DIR="backend"
        elif [[ "$file" == ml/* ]]; then
            DIR="ml"
        else
            continue
        fi

        # Запускаем black check
        if ! black --check --line-length 100 "$file" >/dev/null 2>&1; then
            log_error "Файл $file не отформатирован (black)"
            ERRORS=$((ERRORS + 1))
        fi
    done

    if [ $ERRORS -eq 0 ]; then
        log_success "Форматирование Python соответствует black"
    fi
fi

# Проверка ruff
if ! command_exists ruff; then
    log_warning "ruff не установлен, пропускаем линтинг"
else
    log_info "Линтинг Python (ruff)..."

    for file in "${FILES[@]}"; do
        if ! ruff check "$file" >/dev/null 2>&1; then
            log_error "Файл $file содержит ошибки линтинга (ruff)"
            ERRORS=$((ERRORS + 1))
        fi
    done

    if [ $ERRORS -eq 0 ]; then
        log_success "Линтинг Python пройден (ruff)"
    fi
fi

# Выход с кодом ошибки если были проблемы
if [ $ERRORS -gt 0 ]; then
    log_error "Найдено $ERRORS ошибок валидации Python"
    echo ""
    log_info "Для автоисправления запустите:"
    echo "  cd backend && black --line-length 100 . && ruff check --fix ."
    echo "  cd ml && black --line-length 100 . && ruff check --fix ."
    echo ""
    echo "Или используйте skill: /lint.fix"
    exit 1
fi

exit 0