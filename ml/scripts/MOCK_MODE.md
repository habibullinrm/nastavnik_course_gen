# Mock Mode для ML Pipeline

Mock режим позволяет запускать pipeline без реальных вызовов DeepSeek API, используя заранее подготовленные ответы.

## Преимущества

✅ **Быстро** - генерация за секунды вместо минут
✅ **Бесплатно** - нет затрат на API
✅ **Оффлайн** - работает без интернета
✅ **Предсказуемо** - всегда одинаковые результаты
✅ **CI/CD friendly** - можно использовать в автотестах

## Использование

### Метод 1: Environment variable

```bash
# Установить mock режим
export MOCK_LLM=true

# Запустить pipeline (будет использован mock client)
python3 scripts/run_pipeline_mock.py
```

### Метод 2: Готовый скрипт

```bash
# Скрипт автоматически включает mock режим
docker exec nastavnik_ml python3 scripts/run_pipeline_mock.py
```

### Метод 3: Python API

```python
import os
os.environ["MOCK_LLM"] = "true"

from ml.src.services.llm_client_factory import get_llm_client

# Вернёт MockLLMClient вместо DeepSeekClient
client = await get_llm_client()
```

## Структура Mock Fixtures

```
ml/tests/fixtures/mock_responses/
├── B1_validate.json           # Валидированный профиль
├── B2_competencies.json       # Компетенции
├── B3_ksa_matrix.json         # KSA матрица
├── B4_learning_units.json     # Юниты обучения
├── B5_hierarchy.json          # Иерархия
└── B6_problem_formulations.json  # Проблемные формулировки
```

Каждый файл содержит реальный успешный ответ от DeepSeek, сохранённый из трека `b6d07a75-d4ce-4ce0-b5ae-68e46228de4d`.

## Как работает Mock Client

1. **Определение шага** - анализирует промпт и определяет, какой это этап (B1-B8)
2. **Загрузка fixture** - читает соответствующий JSON из `tests/fixtures/mock_responses/`
3. **Формат ответа** - возвращает в формате OpenAI API (`choices`, `usage`, etc.)
4. **Статистика** - трекает количество вызовов и токенов (эмулированные)

### Определение шага по промпту

```python
# Ключевые слова для каждого шага:
B1_validate         → "validat" + "profile"
B2_competencies     → "competenc" + "formulate"
B3_ksa_matrix       → "ksa" или "decompose" + "competenc"
B4_learning_units   → "learning units" или "theory units"
B5_hierarchy        → "hierarchy" или "leveled"
B6_problem_formulations → "problem formulation" или "blueprints"
B7_schedule         → "schedule" или "weekly"
B8_validation       → "validat" + "track"
```

## Обновление Fixtures

Если изменились промпты и нужны новые fixtures:

```bash
# 1. Запустить real pipeline
docker exec nastavnik_ml python3 -c "
import os
os.environ['MOCK_LLM'] = 'false'  # Явно отключить mock
# ... запустить pipeline
"

# 2. Получить track_id из успешной генерации
TRACK_ID="<новый-track-id>"

# 3. Обновить fixtures
docker exec nastavnik_ml python3 << 'EOF'
import json
from pathlib import Path

track_dir = Path(f'ml/logs/{TRACK_ID}')
fixtures_dir = Path('tests/fixtures/mock_responses')

for log_file in track_dir.glob('step_*.json'):
    with open(log_file) as f:
        log_data = json.load(f)

    fixture_file = fixtures_dir / f'{log_data[\"step_name\"]}.json'
    with open(fixture_file, 'w', encoding='utf-8') as f:
        json.dump(log_data['step_output'], f, indent=2, ensure_ascii=False)
EOF
```

## Тестирование

```bash
# Юнит-тесты mock client
docker exec nastavnik_ml python3 -m pytest tests/test_mock_llm_client.py -v

# Интеграционный тест (полный pipeline)
docker exec nastavnik_ml python3 scripts/run_pipeline_mock.py

# Валидация результата
docker exec nastavnik_ml python3 scripts/validate_pipeline.py \
    --mode logs --track-id <track-id-from-mock-run>
```

## Сравнение режимов

| Характеристика | Real Mode | Mock Mode |
|----------------|-----------|-----------|
| **Скорость** | 2-5 минут | 2-5 секунд |
| **Стоимость** | ~$0.01-0.05 | Бесплатно |
| **Интернет** | Требуется | Не требуется |
| **API ключ** | Требуется | Не требуется |
| **Результаты** | Разные каждый раз | Одинаковые |
| **Для тестирования** | ❌ | ✅ |
| **Для продакшена** | ✅ | ❌ |

## Примеры использования

### Быстрая проверка после изменения промпта

```bash
# 1. Изменить промпт в ml/src/prompts/b3_prompt.py
# 2. Запустить mock pipeline
MOCK_LLM=true python3 scripts/run_pipeline_mock.py

# 3. Валидировать (должны быть 0 ошибок если промпт совместим)
python3 scripts/validate_pipeline.py --mode logs --track-id <id>
```

### CI/CD интеграция

```yaml
# .github/workflows/test-pipeline.yml
- name: Test ML Pipeline
  run: |
    export MOCK_LLM=true
    docker exec nastavnik_ml python3 scripts/run_pipeline_mock.py
    docker exec nastavnik_ml python3 -m pytest tests/pipeline/ -v
```

### Разработка без API ключа

```bash
# Работает даже если DEEPSEEK_API_KEY не установлен
export MOCK_LLM=true
python3 scripts/run_pipeline_mock.py
```

## Ограничения

⚠️ **Mock режим не подходит для:**
- Тестирования изменений в промптах (используются старые ответы)
- Проверки работы с новыми типами профилей
- Валидации реальных LLM ответов

✅ **Mock режим отлично подходит для:**
- Быстрой проверки логики pipeline
- Тестирования валидаторов
- CI/CD автотестов
- Разработки без интернета
- Обучения работе с системой

## Troubleshooting

### Ошибка: "No mock fixture found for step X"

Создайте отсутствующий fixture:
```bash
# Файл должен быть: tests/fixtures/mock_responses/X.json
```

### Ошибка: "Could not detect step from prompt"

Промпт не содержит ключевых слов. Проверьте `_detect_step()` в `mock_llm_client.py` и добавьте новые ключевые слова.

### Mock client возвращает неправильный fixture

Улучшите логику определения в `_detect_step()` - возможно порядок проверок неправильный.

## См. также

- [validate_pipeline.py](./README.md) - валидация результатов
- [mock_llm_client.py](../src/services/mock_llm_client.py) - исходный код
- [test_mock_llm_client.py](../tests/test_mock_llm_client.py) - юнит-тесты
