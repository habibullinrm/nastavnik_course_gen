# API Контракты: Manual Profile Editor (003-manual-profile)

## Существующие эндпоинты (без изменений)

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/profiles` | Загрузка JSON-файла (multipart) |
| `GET` | `/api/profiles` | Список всех профилей |
| `GET` | `/api/profiles/{id}` | Детали профиля |

---

## Новые эндпоинты

### POST /api/profiles/form

Создание профиля из данных формы (JSON body, без файла).

**Request:**
```http
POST /api/profiles/form
Content-Type: application/json

{
  "topic": "Элементы математической логики",
  "subject_area": "Математика",
  "experience_level": "beginner",
  "desired_outcomes": ["Строить таблицы истинности"],
  "target_tasks": [
    { "id": "t1", "description": "Строить таблицы истинности", "complexity_rank": 1 }
  ],
  "task_hierarchy": [
    { "id": "t1", "description": "Строить таблицы истинности", "complexity_rank": 1 }
  ],
  "easiest_task_id": "t1",
  "peak_task_id": "t1",
  "subtasks": [
    {
      "id": "st1",
      "description": "Определить переменные",
      "parent_task_id": "t1",
      "required_skills": [],
      "required_knowledge": []
    }
  ],
  "confusing_concepts": [
    { "id": "c1", "term": "Импликация", "confusion_description": "Почему истинна при ложной посылке?" }
  ],
  "diagnostic_result": "misconceptions",
  "weekly_hours": 5,
  "success_criteria": [
    { "id": "sc1", "description": "Решать задачи без подсказок", "metric": "accuracy >= 0.8", "measurable": true }
  ]
  // ... остальные поля StudentProfileInput (необязательные)
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "topic": "Элементы математической логики",
  "experience_level": "beginner",
  "validation_result": {
    "valid": true,
    "errors": [],
    "warnings": ["Поле 'schedule' не заполнено — расписание будет равномерным"]
  },
  "created_at": "2026-02-18T00:00:00Z"
}
```

**Response 422:**
```json
{
  "detail": [
    { "loc": ["body", "topic"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```

---

### PUT /api/profiles/{id}

Обновление существующего профиля (полная замена data).

**Request:**
```http
PUT /api/profiles/{id}
Content-Type: application/json

{ /* то же тело, что у POST /api/profiles/form */ }
```

**Response 200:**
```json
{
  "id": "uuid",
  "topic": "...",
  "experience_level": "...",
  "validation_result": { "valid": true, "errors": [], "warnings": [] },
  "updated_at": "2026-02-18T01:00:00Z"
}
```

**Response 404:**
```json
{ "detail": "Профиль не найден" }
```

---

## Frontend роутинг (новые страницы)

| Маршрут | Описание |
|---|---|
| `GET /profiles/new` | Пустая форма создания профиля |
| `GET /profiles/[id]/edit` | Форма редактирования с загруженными данными |

### Загрузка профиля для редактирования

Используется существующий `GET /api/profiles/{id}` — возвращает полный `data` JSONB,
который десериализуется в `ProfileFormState`.

### Выбор профиля из БД

Используется существующий `GET /api/profiles` — список всех профилей.
Отображается как выпадающий список или модальное окно выбора на странице `/profiles/new`.

### Выгрузка профиля (браузерный download)

```typescript
// Клиентская функция, без API-запроса
function downloadProfile(state: ProfileFormState): void {
  const slug = state.topic.toLowerCase().replace(/\s+/g, "-").slice(0, 50)
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `profile-${slug}.json`
  a.click()
  URL.revokeObjectURL(url)
}
```

---

## Изменения в profile_service.py

```python
async def create_from_form(
    db: AsyncSession,
    profile_data: StudentProfileInput,
) -> StudentProfile:
    """Создать профиль из данных формы (без загрузки файла).

    Args:
        db: Асинхронная сессия БД.
        profile_data: Данные профиля из формы.

    Returns:
        Созданный профиль.
    """

async def update_profile(
    db: AsyncSession,
    profile_id: UUID,
    profile_data: StudentProfileInput,
) -> StudentProfile:
    """Обновить существующий профиль.

    Args:
        db: Асинхронная сессия БД.
        profile_id: UUID профиля.
        profile_data: Новые данные профиля.

    Returns:
        Обновлённый профиль.

    Raises:
        ValueError: Если профиль не найден.
    """
```