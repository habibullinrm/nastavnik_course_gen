# E2E тесты с Playwright

Автоматизированные UI тесты для фронтенда наставник_course_gen.

## Установка

```bash
# Установить зависимости
npm install

# Установить браузеры Playwright
npm run playwright:install
```

## Запуск тестов

```bash
# Запуск всех E2E тестов (headless mode)
npm run test:e2e

# Запуск с UI режимом (для дебаггинга)
npm run test:e2e:ui

# Запуск с видимым браузером
npm run test:e2e:headed

# Запуск конкретного теста
npx playwright test profile-upload.spec.ts

# Запуск с конкретным браузером
npx playwright test --project=chromium
```

## Структура тестов

```
tests/
├── e2e/
│   ├── profile-upload.spec.ts     # Тесты компонента ProfileUpload
│   └── generation-progress.spec.ts # Тесты страницы генерации
├── fixtures/                       # Тестовые данные (JSON профили)
└── README.md                       # Эта документация
```

## Покрытие тестов

### profile-upload.spec.ts
- ✅ Загрузка главной страницы
- ✅ Отображение заголовков h1/h2
- ✅ Наличие file input с правильными атрибутами
- ✅ Отображение label для file input
- ✅ Навигационное меню (4 ссылки)
- ✅ Tailwind CSS стили
- ✅ Навигация на /tracks
- ⏸️ Загрузка JSON файла (skip, требует fixtures)

### generation-progress.spec.ts
- ✅ Страница с profile_id параметром
- ✅ Ошибка при отсутствии profile_id
- ⏸️ Отображение прогресса (skip, требует SSE моки)
- ⏸️ Редирект после завершения (skip, требует моки)

## Требования для запуска

1. **Frontend сервер должен быть запущен:**
   ```bash
   # В Docker
   docker compose up frontend

   # Или локально
   npm run dev
   ```

2. **Backend API должен быть доступен** (для тестов с загрузкой профиля):
   ```bash
   docker compose up backend db
   ```

## Отчёты

После запуска тестов:
- HTML отчёт: `playwright-report/index.html`
- Скриншоты падений: `test-results/`
- Видео (при падении): `test-results/*/video.webm`

Открыть HTML отчёт:
```bash
npx playwright show-report
```

## Переменные окружения

```bash
# Базовый URL для тестов (по умолчанию http://localhost:3000)
export PLAYWRIGHT_BASE_URL=http://localhost:3000

# Запуск в CI режиме (больше retries, sequential execution)
export CI=true
```

## Дебаггинг

```bash
# Режим отладки с паузами
npx playwright test --debug

# Trace viewer для анализа падений
npx playwright show-trace test-results/<test-name>/trace.zip
```

## TODO

- [ ] Добавить fixtures для тестовых JSON профилей
- [ ] Реализовать моки для SSE endpoints
- [ ] Добавить тесты для валидации ошибок
- [ ] Добавить тесты для компонента GenerationProgress
- [ ] Интеграция с CI/CD pipeline
- [ ] Visual regression тесты (скриншоты)
- [ ] Accessibility тесты (axe-core)

## Полезные ссылки

- [Playwright документация](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Локаторы](https://playwright.dev/docs/locators)
