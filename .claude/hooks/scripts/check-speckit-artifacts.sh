#!/usr/bin/env bash
# check-speckit-artifacts.sh - Проверка структуры SpecKit артефактов

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

log_info "Проверка структуры SpecKit артефактов..."

for file in "${FILES[@]}"; do
    # Проверяем только файлы в specs/
    if [[ ! "$file" =~ ^specs/ ]]; then
        continue
    fi

    # Валидный паттерн: specs/###-feature-name/(spec|plan|tasks).md
    # Разрешаем также вспомогательные файлы (research.md, quickstart.md, data-model.md, checklists/*)
    if [[ "$file" =~ ^specs/[0-9]{3}-[a-z0-9-]+/(spec|plan|tasks)\.md$ ]] || \
       [[ "$file" =~ ^specs/[0-9]{3}-[a-z0-9-]+/(research|quickstart|data-model)\.md$ ]] || \
       [[ "$file" =~ ^specs/[0-9]{3}-[a-z0-9-]+/checklists/ ]]; then
        # Файл соответствует структуре
        continue
    else
        log_error "Файл $file не соответствует структуре SpecKit"
        echo "  Ожидается: specs/###-feature-name/(spec|plan|tasks).md"
        echo "  Или вспомогательные: research.md, quickstart.md, data-model.md, checklists/*"
        echo "  Пример: specs/001-user-auth/spec.md"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -gt 0 ]; then
    log_error "Найдено $ERRORS ошибок структуры SpecKit"
    exit 1
fi

if [ ${#FILES[@]} -gt 0 ]; then
    log_success "Структура SpecKit артефактов корректна"
fi

exit 0