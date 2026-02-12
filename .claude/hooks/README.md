# Git Hooks для nastavnik_course_gen

Автоматическая валидация кода и соблюдения конституции проекта при коммитах и push.

## Установка

```bash
bash .claude/hooks/install.sh
```

Скрипт установит все хуки в `.git/hooks/` и сделает их исполняемыми.

## Хуки

### pre-commit

Запускается перед каждым коммитом и выполняет валидацию staged файлов:

**Python файлы:**
- ✅ Форматирование (black --check --line-length 100)
- ✅ Линтинг (ruff check)
- ⚠️ Проверка async-first нарушений (блокирующие вызовы)

**TypeScript файлы:**
- ✅ Линтинг (eslint)
- ✅ Type checking (tsc --noEmit)

**SpecKit артефакты:**
- ✅ Проверка структуры (specs/###-feature-name/*.md)

**Async-first проверка:**

Ищет блокирующие вызовы в Python коде:
- `requests.*` → альтернатива: `httpx` (async HTTP)
- `time.sleep` → альтернатива: `asyncio.sleep`
- `open()` → альтернатива: `aiofiles`
- `sqlite3.*` → альтернатива: `aiosqlite`

При обнаружении предлагает продолжить или отменить коммит.

### commit-msg

Проверяет сообщение коммита на соответствие **Принципу IV конституции** (русский язык):

- ✅ Минимальная длина: 10 символов
- ✅ Минимум 3 кириллических символа
- ⏭️ Пропускает Merge/Revert коммиты

**Примеры правильных сообщений:**
```
добавлена функция валидации профилей
исправлена ошибка в алгоритме генерации курса
обновлена документация Phase A
```

**Примеры неправильных:**
```
add validation     ❌ (английский язык)
fix                ❌ (слишком короткое)
test123            ❌ (нет кириллицы)
```

### pre-push

Запускается перед push и выполняет финальные проверки:

- ✅ Запуск pytest для backend (если есть tests/)
- ✅ Запуск pytest для ml (если есть tests/)
- ✅ Валидация docker-compose.yml
- ✅ Проверка наличия Dockerfile для сервисов

## Отключение хуков

В редких случаях (emergency fix, merge conflicts) можно пропустить хуки:

```bash
git commit --no-verify -m "срочное исправление"
git push --no-verify
```

**⚠️ Не рекомендуется** использовать регулярно - хуки обеспечивают качество кода.

## Обновление хуков

После изменения скриптов в `.claude/hooks/`:

```bash
bash .claude/hooks/install.sh
```

Установщик создаёт backup существующих хуков (.backup).

## Структура

```
.claude/hooks/
├── pre-commit              # Основной хук
├── commit-msg              # Проверка commit message
├── pre-push                # Запуск тестов
├── install.sh              # Установщик
├── README.md               # Документация (этот файл)
└── scripts/                # Вспомогательные скрипты
    ├── common.sh           # Функции логирования
    ├── validate-python.sh  # Black + Ruff
    ├── validate-typescript.sh  # ESLint + tsc
    ├── check-async-violations.sh  # Async-first
    ├── check-russian-commit.sh  # Русский язык
    ├── check-speckit-artifacts.sh  # SpecKit структура
    └── docker-health-check.sh  # Docker валидация
```

## Ручной запуск валидации

Можно запускать скрипты вручную для проверки:

```bash
# Проверка Python файлов
bash .claude/hooks/scripts/validate-python.sh backend/src/*.py

# Проверка commit message
bash .claude/hooks/scripts/check-russian-commit.sh "тестовое сообщение"

# Проверка async-first
bash .claude/hooks/scripts/check-async-violations.sh backend/src/*.py

# Проверка Docker
bash .claude/hooks/scripts/docker-health-check.sh
```

## Troubleshooting

### Проблема: Pre-commit hook не срабатывает

**Проверка:**
```bash
ls -la .git/hooks/pre-commit
```

**Решение:**
```bash
bash .claude/hooks/install.sh
```

### Проблема: "black не установлен"

**Решение:**
```bash
cd backend
pip install black ruff
```

### Проблема: "eslint не установлен"

**Решение:**
```bash
cd frontend
npm install
```

### Проблема: Хук блокирует легитимный код

**Временное отключение:**
```bash
git commit --no-verify -m "легитимное использование requests в тестах"
```

**Долгосрочное решение:**
- Тесты (в директориях `tests/` или файлах `test_*.py`) автоматически пропускаются
- Для других случаев - добавить исключение в скрипт

## Интеграция с конституцией

Хуки обеспечивают соблюдение принципов конституции проекта (`.specify/memory/constitution.md`):

- **Принцип I** (Container Isolation) - проверка Docker конфигурации
- **Принцип II** (Explicit Dependencies) - косвенная проверка через тесты
- **Принцип III** (Async-First Architecture) - поиск блокирующих вызовов
- **Принцип IV** (Russian Language) - проверка commit messages и docstrings
- **Принцип V** (Deepseek LLM Only) - проверка через `/validate.constitution` skill

## Claude Skills для работы с хуками

Доступны следующие skills:

- `/lint.fix` - автоисправление ошибок форматирования
- `/validate.constitution` - полная проверка конституции
- `/test.all` - запуск всех тестов (backend + ml + frontend)

## Дополнительно

- Хуки работают локально (не влияют на других разработчиков)
- Можно создать `.git/hooks/skip-hooks` для временного отключения всех хуков
- Логи хуков цветные для лучшей читаемости (зелёный ✓, красный ✗, жёлтый ⚠️)