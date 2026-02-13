/**
 * E2E тесты для компонента ProfileUpload.
 *
 * Тестирует:
 * - Загрузку главной страницы
 * - Отображение компонента загрузки профиля
 * - Функционал file input
 * - Навигацию
 */

import { test, expect } from '@playwright/test';

test.describe('ProfileUpload Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('должен отобразить главную страницу с правильным заголовком', async ({ page }) => {
    await expect(page).toHaveTitle(/Nastavnik/);

    const h1 = page.locator('h1');
    await expect(h1).toContainText('Сервис тестирования алгоритма генерации учебных треков');
  });

  test('должен отобразить компонент загрузки профиля', async ({ page }) => {
    const h2 = page.locator('h2');
    await expect(h2).toContainText('Загрузка профиля студента');

    const fileInput = page.locator('input[type="file"]#file-upload');
    await expect(fileInput).toBeAttached();
    await expect(fileInput).toHaveAttribute('accept', '.json');
  });

  test('должен иметь label для file input', async ({ page }) => {
    const label = page.locator('label[for="file-upload"]');
    await expect(label).toBeVisible();
    await expect(label).toContainText('JSON файл');
  });

  test('должен отображать навигационное меню', async ({ page }) => {
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();

    // Проверка всех ссылок навигации
    await expect(page.locator('nav >> text=Загрузка')).toBeVisible();
    await expect(page.locator('nav >> text=Треки')).toBeVisible();
    await expect(page.locator('nav >> text=QA')).toBeVisible();
    await expect(page.locator('nav >> text=Профили')).toBeVisible();
  });

  test('должен иметь корректные стили Tailwind CSS', async ({ page }) => {
    const uploadBox = page.locator('.border-dashed');
    await expect(uploadBox).toBeVisible();

    const label = page.locator('label[for="file-upload"]');
    const className = await label.getAttribute('class');
    expect(className).toContain('text-blue-600');
  });

  test('навигация должна работать (переход на /tracks)', async ({ page }) => {
    await page.click('nav >> text=Треки');
    await page.waitForURL('**/tracks');
    expect(page.url()).toContain('/tracks');
  });

  test.skip('должен загрузить JSON файл и показать кнопку генерации', async ({ page }) => {
    // Этот тест требует создания тестового JSON файла
    // и моков для API запросов

    const fileInput = page.locator('input[type="file"]#file-upload');

    // TODO: Создать тестовый profile.json
    // await fileInput.setInputFiles('./tests/fixtures/test-profile.json');

    // TODO: Проверить отображение validation result
    // const validationSuccess = page.locator('text=Профиль валиден');
    // await expect(validationSuccess).toBeVisible();

    // TODO: Проверить кнопку "Сгенерировать трек"
    // const generateButton = page.locator('button:has-text("Сгенерировать трек")');
    // await expect(generateButton).toBeVisible();
  });
});
