#!/usr/bin/env bash
# validate-typescript.sh - Валидация TypeScript кода (eslint, tsc)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Проверка наличия frontend директории
FRONTEND_DIR="$(get_git_root)/frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
    log_info "Директория frontend/ не найдена, пропускаем валидацию TypeScript"
    exit 0
fi

# Проверка наличия package.json
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    log_info "package.json не найден, пропускаем валидацию TypeScript"
    exit 0
fi

cd "$FRONTEND_DIR"

ERRORS=0

# Проверка наличия node_modules
if [ ! -d "node_modules" ]; then
    log_warning "node_modules не найдены, запустите: cd frontend && npm install"
    exit 0
fi

# ESLint
log_info "Линтинг TypeScript (eslint)..."
if npm run lint >/dev/null 2>&1; then
    log_success "ESLint пройден"
else
    log_error "ESLint обнаружил ошибки"
    ERRORS=$((ERRORS + 1))
fi

# Type checking
log_info "Проверка типов TypeScript (tsc)..."
if npm run type-check >/dev/null 2>&1; then
    log_success "Type checking пройден"
else
    log_error "Type checking обнаружил ошибки"
    ERRORS=$((ERRORS + 1))
fi

# Выход с кодом ошибки если были проблемы
if [ $ERRORS -gt 0 ]; then
    log_error "Найдено $ERRORS ошибок валидации TypeScript"
    echo ""
    log_info "Для автоисправления запустите:"
    echo "  cd frontend && npm run lint -- --fix"
    exit 1
fi

exit 0