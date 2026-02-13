# ML Pipeline Validation Script (MVP)

Тестовый скрипт для валидации корректности форматов данных в ML pipeline (этапы B1-B8).

## Возможности MVP версии

- ✅ **Schema Validation**: Проверка соответствия Pydantic схемам
- ✅ **Reference Validation**: Проверка целостности ID ссылок между этапами
- ✅ **Console Output**: Красивый цветной вывод через Rich
- ✅ **JSON/Text Export**: Сохранение отчётов в файлы
- ✅ **Pytest Tests**: Базовые тесты для валидаторов

## Установка

```bash
# Установить зависимости
cd ml
pip install -e ".[dev]"

# Или через poetry/uv если используются
```

## Использование

### Режим 1: Валидация существующих логов

Проверка логов уже сгенерированного трека:

```bash
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id e30c05f4-1f18-4cc6-af2c-3b9b441c80fd
```

С подробным выводом:

```bash
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id e30c05f4-1f18-4cc6-af2c-3b9b441c80fd \
    --verbose
```

Валидация только определённых этапов:

```bash
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id e30c05f4-1f18-4cc6-af2c-3b9b441c80fd \
    --steps B1_validate,B2_competencies,B3_ksa_matrix
```

### Режим 2: Валидация mock данных

Проверка тестовых данных (для разработки):

```bash
python ml/scripts/validate_pipeline.py \
    --mode mock \
    --mock-data ml/tests/fixtures/test_data.json
```

### Форматы вывода

**Console (по умолчанию):**

```bash
python ml/scripts/validate_pipeline.py --mode logs --track-id <id>
```

**JSON (для CI/CD):**

```bash
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id <id> \
    --output-format json \
    --output-file validation_report.json
```

**Text (для логов):**

```bash
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id <id> \
    --output-format text \
    --output-file validation_report.txt
```

## Типы проверок

### Schema Validation (SchemaValidator)

Проверяет соответствие данных Pydantic схемам из `ml/src/schemas/pipeline_steps.py`:

- Все обязательные поля присутствуют
- Типы данных корректны
- Constraints соблюдены (min/max values)
- Nested models валидны

**Пример ошибки:**

```
✗ B1_validate: Schema Field Validation
  Field 'effective_level': field required
  Recommendation: Fix field 'effective_level' in step output or update schema
```

### Reference Validation (ReferenceValidator)

Проверяет целостность ID ссылок:

**B2 → B3:** Компетенции используются в KSA матрице
**B3 internal:**
- Knowledge → Skills/Habits ссылки корректны
- Skills → Knowledge ссылки корректны
- Skills → Habits ссылки корректны
- Habits → Skills ссылки корректны
- Dependency graph содержит валидные IDs

**B4 → B5:**
- unit_sequence содержит только units из B4
- Нет дублирующихся IDs
- Все units из B4 присутствуют в sequence

**Пример ошибки:**

```
✗ B3: Knowledge Required For
  Knowledge k1 references unknown ID s999
  Expected: Valid skill or habit ID
  Actual: s999
  Recommendation: Add skill/habit s999 or fix reference
```

## Exit Codes

- `0` - Все проверки пройдены
- `1` - Есть failed checks (warnings)
- `2` - Есть critical failures
- `3` - Ошибка выполнения скрипта

## Запуск тестов

```bash
# Все тесты для pipeline validation
cd ml
pytest tests/pipeline/ -v

# С покрытием кода
pytest tests/pipeline/ -v --cov=scripts/validators

# Только schema validation тесты
pytest tests/pipeline/test_schema_validation.py -v

# Только reference validation тесты
pytest tests/pipeline/test_reference_validation.py -v
```

## Структура проекта

```
ml/
├── scripts/
│   ├── validate_pipeline.py         # CLI entry point
│   ├── README.md                    # Эта документация
│   └── validators/
│       ├── __init__.py
│       ├── base.py                  # ValidationCheck, ValidationReport
│       ├── schema_validator.py      # Pydantic validation
│       ├── reference_validator.py   # ID integrity checks
│       └── report_generator.py      # Console/JSON/Text reports
└── tests/
    └── pipeline/
        ├── conftest.py              # Pytest fixtures
        ├── test_schema_validation.py
        └── test_reference_validation.py
```

## Примеры использования

### CI/CD интеграция

```bash
#!/bin/bash
# .github/workflows/validate-pipeline.sh

TRACK_ID="e30c05f4-1f18-4cc6-af2c-3b9b441c80fd"

python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id $TRACK_ID \
    --output-format json \
    --output-file pipeline_validation.json

EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo "CRITICAL: Pipeline validation failed with critical errors!"
    exit 1
elif [ $EXIT_CODE -eq 1 ]; then
    echo "WARNING: Pipeline validation completed with warnings"
fi

exit 0
```

### Отладка промптов

После изменения промптов проверить, что pipeline всё ещё генерирует корректные данные:

```bash
# 1. Запустить pipeline с тестовым профилем
curl -X POST http://localhost:8001/pipeline/run \
    -H "Content-Type: application/json" \
    -d @docs/test_profile_1.json

# 2. Получить track_id из ответа
TRACK_ID="<new-track-id>"

# 3. Валидировать результат
python ml/scripts/validate_pipeline.py \
    --mode logs \
    --track-id $TRACK_ID \
    --verbose
```

## Будущие улучшения (не в MVP)

- 🔲 **GraphValidator**: Детекция циклов в dependency_graph
- 🔲 **BusinessValidator**: Time budgets, coverage checks, level alignment
- 🔲 **HTML Dashboard**: Интерактивные отчёты с графиками
- 🔲 **Live Mode**: Генерация + валидация в реальном времени
- 🔲 **Автоисправление**: Предложение патчей для типичных ошибок

## Troubleshooting

### Ошибка: "Track directory not found"

Убедитесь, что логи сохраняются в правильной директории:

```bash
ls -la ml/ml/logs/<track-id>/
```

Путь должен быть: `ml/ml/logs/{track_id}/step_*.json`

### Ошибка: "No schema defined for step"

Проверьте, что `step_name` в логах соответствует ключам в `SCHEMA_MAP`:

```python
# Валидные step names:
"B1_validate", "B2_competencies", "B3_ksa_matrix",
"B4_learning_units", "B5_hierarchy", "B6_problem_formulations",
"B7_schedule", "B8_validation"
```

### Много warnings о непокрытых компетенциях (B2→B3)

Это нормально на ранних этапах - не все компетенции обязательно явно упоминаются в B3 источниках. Это warnings, не critical errors.

## Поддержка

Вопросы и баги: создайте issue в репозитории или обратитесь к команде разработки.
