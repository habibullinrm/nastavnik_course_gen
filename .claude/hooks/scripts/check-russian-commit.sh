#!/usr/bin/env bash
# check-russian-commit.sh - Проверка русского языка в commit message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Использование: $0 <commit-message-file>"
    exit 1
fi

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Пропускаем Merge/Revert коммиты
if [[ "$COMMIT_MSG" =~ ^Merge ]] || [[ "$COMMIT_MSG" =~ ^Revert ]]; then
    log_info "Пропускаем проверку для Merge/Revert коммита"
    exit 0
fi

# Извлекаем первую строку (заголовок)
FIRST_LINE=$(echo "$COMMIT_MSG" | head -n 1)

# Проверка минимальной длины
MIN_LENGTH=10
if [ ${#FIRST_LINE} -lt $MIN_LENGTH ]; then
    log_error "Сообщение коммита слишком короткое (минимум $MIN_LENGTH символов)"
    echo "  Ваше: '$FIRST_LINE' (${#FIRST_LINE} символов)"
    exit 1
fi

# Подсчёт кириллических символов
CYRILLIC_COUNT=$(echo "$FIRST_LINE" | grep -o '[А-Яа-яЁё]' | wc -l)
MIN_CYRILLIC=3

if [ "$CYRILLIC_COUNT" -lt $MIN_CYRILLIC ]; then
    log_error "Сообщение коммита должно быть на русском языке (Принцип IV конституции)"
    echo "  Найдено кириллических символов: $CYRILLIC_COUNT (минимум $MIN_CYRILLIC)"
    echo "  Ваше: '$FIRST_LINE'"
    echo ""
    log_info "Примеры правильных сообщений:"
    echo "  - добавлена функция валидации профилей"
    echo "  - исправлена ошибка в алгоритме генерации курса"
    echo "  - обновлена документация Phase A"
    exit 1
fi

log_success "Сообщение коммита соответствует требованиям (русский язык)"
exit 0