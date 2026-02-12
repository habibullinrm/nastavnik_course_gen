#!/usr/bin/env bash
# docker-health-check.sh - Проверка Docker конфигурации

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

GIT_ROOT=$(get_git_root)
ERRORS=0

log_info "Проверка Docker конфигурации..."

# Проверка наличия docker-compose
if ! command_exists docker; then
    log_warning "Docker не установлен, пропускаем проверку"
    exit 0
fi

# Проверка валидности docker-compose.yml
if [ -f "$GIT_ROOT/docker-compose.yml" ]; then
    log_info "Валидация docker-compose.yml..."

    if docker compose config >/dev/null 2>&1; then
        log_success "docker-compose.yml валиден"
    else
        log_error "docker-compose.yml содержит ошибки"
        ERRORS=$((ERRORS + 1))
    fi
else
    log_warning "docker-compose.yml не найден"
fi

# Проверка наличия Dockerfile для каждого сервиса
SERVICES=("backend" "ml" "frontend")

for service in "${SERVICES[@]}"; do
    if [ -d "$GIT_ROOT/$service" ]; then
        if [ -f "$GIT_ROOT/$service/Dockerfile" ]; then
            log_success "Dockerfile для $service существует"
        else
            log_warning "Dockerfile для $service не найден"
        fi
    fi
done

# Выход с кодом ошибки если были проблемы
if [ $ERRORS -gt 0 ]; then
    log_error "Проверка Docker конфигурации не пройдена"
    exit 1
fi

exit 0