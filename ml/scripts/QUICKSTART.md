# Quick Start: Pipeline Validator

## Быстрый старт (1 минута)

### Проверить существующий трек

```bash
docker exec nastavnik_ml python3 scripts/validate_pipeline.py \
    --mode logs \
    --track-id e30c05f4-1f18-4cc6-af2c-3b9b441c80fd
```

### Запустить тесты

```bash
docker exec nastavnik_ml python3 -m pytest tests/pipeline/ -v
```

## Основные команды

### Валидация с подробным выводом

```bash
docker exec nastavnik_ml python3 scripts/validate_pipeline.py \
    --mode logs \
    --track-id <track-id> \
    --verbose
```

### Экспорт в JSON

```bash
docker exec nastavnik_ml python3 scripts/validate_pipeline.py \
    --mode logs \
    --track-id <track-id> \
    --output-format json \
    --output-file /tmp/report.json
```

### Проверка только определённых этапов

```bash
docker exec nastavnik_ml python3 scripts/validate_pipeline.py \
    --mode logs \
    --track-id <track-id> \
    --steps B1_validate,B2_competencies,B3_ksa_matrix
```

## Exit codes

- `0` = ✅ Все проверки пройдены
- `1` = ⚠️  Есть warnings
- `2` = ❌ Есть критические ошибки
- `3` = 💥 Ошибка выполнения

## Подробная документация

См. [README.md](./README.md) и [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md)
