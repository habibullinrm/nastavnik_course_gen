/**
 * E2E тесты для страницы генерации трека.
 *
 * Тестирует:
 * - Страницу /tracks/generate
 * - Отображение прогресса
 * - SSE обновления (требует моки)
 */

import { test, expect } from '@playwright/test';

test.describe('Generation Progress Page', () => {
  test('должен отобразить страницу генерации с параметром profile_id', async ({ page }) => {
    const testProfileId = 'test-profile-123';
    await page.goto(`http://localhost:3000/tracks/generate?profile_id=${testProfileId}`);

    // Проверка Suspense fallback
    const loading = page.locator('text=Загрузка');
    await expect(loading).toBeVisible();
  });

  test('должен показать ошибку если profile_id отсутствует', async ({ page }) => {
    await page.goto('http://localhost:3000/tracks/generate');

    // Ожидаем сообщение об ошибке
    const errorMessage = page.locator('text=Profile ID not provided');
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test.skip('должен отображать прогресс генерации (требует мок SSE)', async ({ page }) => {
    // TODO: Реализовать моки для SSE endpoint
    // TODO: Проверить отображение шагов B1-B8
    // TODO: Проверить прогресс-бар
  });

  test.skip('должен перенаправить на страницу трека после завершения', async ({ page }) => {
    // TODO: Мок успешной генерации
    // TODO: Проверка редиректа на /tracks/{track_id}
  });
});
