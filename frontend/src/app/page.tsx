/**
 * Главная страница — лендинг сервиса тестирования алгоритма.
 */

import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 p-8">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Генератор учебных треков
        </h1>
        <p className="text-lg text-gray-500 mb-10">
          Тестирование алгоритма персонализированной генерации курсов (pipeline B1–B8)
        </p>

        <Link
          href="/profiles"
          className="inline-block px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-md"
        >
          Выбрать профиль для генерации →
        </Link>

        <div className="mt-12 text-left bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Как это работает
          </h2>
          <ol className="space-y-3">
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-7 h-7 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-bold">1</span>
              <div>
                <p className="text-sm font-medium text-gray-800">Создать или выбрать профиль</p>
                <p className="text-xs text-gray-500 mt-0.5">Заполните форму профиля студента или выберите готовый из базы</p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-7 h-7 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-bold">2</span>
              <div>
                <p className="text-sm font-medium text-gray-800">Запустить генерацию трека</p>
                <p className="text-xs text-gray-500 mt-0.5">Алгоритм прогонит pipeline из 8 шагов и сформирует персонализированный учебный трек</p>
              </div>
            </li>
            <li className="flex gap-3">
              <span className="flex-shrink-0 w-7 h-7 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-bold">3</span>
              <div>
                <p className="text-sm font-medium text-gray-800">Провести отладку при необходимости</p>
                <p className="text-xs text-gray-500 mt-0.5">Используйте ручной режим для тестирования отдельных шагов и редактирования промптов</p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </main>
  )
}
