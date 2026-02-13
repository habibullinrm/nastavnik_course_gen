/**
 * Конфигурация Playwright для E2E тестов.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',

  // Timeout для каждого теста
  timeout: 30 * 1000,

  // Ожидание действий (click, fill, etc.)
  expect: {
    timeout: 5000,
  },

  // Запускать тесты последовательно (для стабильности)
  fullyParallel: false,

  // Количество повторных попыток при падении теста
  retries: process.env.CI ? 2 : 0,

  // Количество параллельных workers
  workers: process.env.CI ? 1 : undefined,

  // Репортеры
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // Настройки для всех тестов
  use: {
    // Базовый URL (можно переопределить через env)
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

    // Скриншоты только при падении
    screenshot: 'only-on-failure',

    // Видео только при падении
    video: 'retain-on-failure',

    // Trace для дебаггинга
    trace: 'on-first-retry',
  },

  // Проекты (браузеры)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Раскомментируйте для тестирования в других браузерах
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Web сервер (опционально, если нужно запускать dev server автоматически)
  // webServer: {
  //   command: 'npm run dev',
  //   port: 3000,
  //   reuseExistingServer: !process.env.CI,
  // },
});
