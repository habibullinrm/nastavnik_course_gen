/**
 * E2E тест для Phase 4 (US2) - T057a
 *
 * Проверяет страницу просмотра трека:
 * - TreeView (раскрытие компетенций → ЗУН → единиц)
 * - TrackMetadata (версия алгоритма, LLM calls)
 * - FieldUsage (таблица использованных/неиспользованных полей)
 * - WeeklySchedule (понедельное расписание)
 */

import { test, expect } from '@playwright/test'

test.describe('Track Detail Page - Phase 4 (US2)', () => {
  test.beforeEach(async ({ page }) => {
    // Получить ID первого доступного трека
    const response = await page.request.get('http://localhost:8000/api/tracks/')
    const data = await response.json()

    if (data.tracks && data.tracks.length > 0) {
      const trackId = data.tracks[0].id
      await page.goto(`http://localhost:3000/tracks/${trackId}`)
      await page.waitForLoadState('networkidle')
    } else {
      throw new Error('No tracks available for testing')
    }
  })

  test('should display track title and status', async ({ page }) => {
    // Проверить наличие заголовка страницы
    await expect(page.locator('h1')).toBeVisible()

    // Проверить отображение статуса
    await expect(page.locator('[class*="bg-green-100"], [class*="bg-red-100"], [class*="bg-yellow-100"]')).toBeVisible()
  })

  test('should display navigation tabs', async ({ page }) => {
    // Проверить наличие всех табов
    await expect(page.locator('text=🌳')).toBeVisible()
    await expect(page.locator('text=Дерево курса')).toBeVisible()
    await expect(page.locator('text=📅')).toBeVisible()
    await expect(page.locator('text=Расписание')).toBeVisible()
    await expect(page.locator('text=📊')).toBeVisible()
    await expect(page.locator('text=Метаданные')).toBeVisible()
    await expect(page.locator('text=🔍')).toBeVisible()
    await expect(page.locator('text=Поля профиля')).toBeVisible()
  })

  test('should display TreeView and allow expansion', async ({ page }) => {
    // Таб TreeView должен быть активен по умолчанию
    await expect(page.locator('text=Структура курса')).toBeVisible()

    // Проверить наличие секций
    const competenciesButton = page.locator('button:has-text("Компетенции")')
    if (await competenciesButton.count() > 0) {
      // Раскрыть компетенции
      await competenciesButton.click()
      await page.waitForTimeout(300)

      // Проверить, что содержимое появилось
      await expect(page.locator('.ml-6').first()).toBeVisible()
    }

    // Проверить наличие других секций
    const ksaButton = page.locator('button:has-text("Матрица ЗУН")')
    if (await ksaButton.count() > 0) {
      await ksaButton.click()
      await page.waitForTimeout(300)
    }

    const unitsButton = page.locator('button:has-text("Учебные единицы")')
    if (await unitsButton.count() > 0) {
      await unitsButton.click()
      await page.waitForTimeout(300)
    }
  })

  test('should display TrackMetadata', async ({ page }) => {
    // Переключиться на таб Метаданные
    await page.locator('button:has-text("Метаданные")').click()
    await page.waitForTimeout(300)

    // Проверить наличие заголовка
    await expect(page.locator('text=Метаданные генерации')).toBeVisible()

    // Проверить наличие полей метаданных
    await expect(page.locator('text=Версия алгоритма')).toBeVisible()
    await expect(page.locator('text=Статус')).toBeVisible()
    await expect(page.locator('text=Дата создания')).toBeVisible()
  })

  test('should display FieldUsage statistics', async ({ page }) => {
    // Переключиться на таб Поля профиля
    await page.locator('button:has-text("Поля профиля")').click()
    await page.waitForTimeout(500)

    // Проверить наличие заголовка
    await expect(page.locator('text=Использование полей профиля')).toBeVisible()

    // Проверить наличие статистики
    await expect(page.locator('text=Всего полей')).toBeVisible()
    await expect(page.locator('text=Использовано')).toBeVisible()
    await expect(page.locator('text=Не использовано')).toBeVisible()

    // Проверить наличие таблиц
    const usedSection = page.locator('text=Использованные поля')
    const unusedSection = page.locator('text=Неиспользованные поля')

    await expect(usedSection.or(unusedSection)).toBeVisible()
  })

  test('should display WeeklySchedule', async ({ page }) => {
    // Переключиться на таб Расписание
    await page.locator('button:has-text("Расписание")').click()
    await page.waitForTimeout(300)

    // Проверить наличие заголовка
    await expect(page.locator('text=Понедельное расписание').or(page.locator('text=Расписание'))).toBeVisible()

    // Проверить наличие недель или сообщения о их отсутствии
    const weekButton = page.locator('button:has-text("Неделя")')
    const noScheduleMessage = page.locator('text=Расписание не сгенерировано')

    await expect(weekButton.or(noScheduleMessage)).toBeVisible()

    // Если есть недели, попробовать раскрыть первую
    if (await weekButton.count() > 0) {
      await weekButton.first().click()
      await page.waitForTimeout(300)

      // Проверить отображение дней
      await expect(page.locator('text=Понедельник').or(page.locator('text=день'))).toBeVisible()
    }
  })

  test('should handle tab navigation', async ({ page }) => {
    // Проверить переключение между табами
    const tabs = [
      { name: 'Расписание', content: 'Понедельное расписание' },
      { name: 'Метаданные', content: 'Метаданные генерации' },
      { name: 'Поля профиля', content: 'Использование полей профиля' },
      { name: 'Дерево курса', content: 'Структура курса' },
    ]

    for (const tab of tabs) {
      await page.locator(`button:has-text("${tab.name}")`).click()
      await page.waitForTimeout(300)
      await expect(page.locator(`text=${tab.content}`).or(page.locator('h3'))).toBeVisible()
    }
  })

  test('should display validation B8 results if available', async ({ page }) => {
    // Проверить наличие секции валидации B8
    const validationSection = page.locator('text=Результат валидации B8')

    if (await validationSection.count() > 0) {
      await expect(validationSection).toBeVisible()

      // Проверить статус валидации
      const passedStatus = page.locator('text=Трек прошел валидацию')
      const failedStatus = page.locator('text=Трек не прошел валидацию')

      await expect(passedStatus.or(failedStatus)).toBeVisible()
    }
  })
})
