/**
 * Страница QA - пакетная генерация и контроль качества
 *
 * Позволяет запустить пакетную генерацию N версий трека из одного профиля
 * и отображает список предыдущих QA-отчётов.
 */

'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

interface QAReportSummary {
  id: string
  profile_id: string
  topic: string
  batch_size: number
  completed_count: number
  mean_cdv: number | null
  recommendation: string | null
  status: string
  created_at: string
}

export default function QAPage() {
  const [reports, setReports] = useState<QAReportSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchReports()
  }, [])

  async function fetchReports() {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
      const response = await fetch(`${apiUrl}/api/qa/reports/`)
      if (response.status === 404) {
        // API не реализовано пока - Phase 5
        setReports([])
        return
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const data = await response.json()
      setReports(data.reports || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки QA-отчётов')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-600">Загрузка QA-отчётов...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Контроль качества (QA)</h1>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">
          Пакетная генерация
        </h2>
        <p className="text-blue-700 mb-4">
          Запустите генерацию нескольких версий трека из одного профиля для оценки стабильности алгоритма.
          Система рассчитает коэффициент различия версий (CDV) и даст рекомендацию.
        </p>
        <p className="text-sm text-blue-600">
          <strong>Статус:</strong> Функционал будет доступен в Phase 5 (US3)
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
          <h2 className="font-semibold mb-2">Ошибка</h2>
          <p>{error}</p>
        </div>
      )}

      {reports.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 mb-4">Пока нет QA-отчётов</p>
          <p className="text-sm text-gray-500">
            Пакетная генерация будет доступна после реализации Phase 5 (US3)
          </p>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Тема
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Размер батча
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Завершено
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CDV
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Рекомендация
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Дата
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reports.map((report) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/qa/${report.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {report.topic}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.batch_size}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.completed_count} / {report.batch_size}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {report.mean_cdv !== null ? `${(report.mean_cdv * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {report.recommendation && (
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full
                        ${report.recommendation === 'stable' ? 'bg-green-100 text-green-800' : ''}
                        ${report.recommendation === 'needs_improvement' ? 'bg-yellow-100 text-yellow-800' : ''}
                        ${report.recommendation === 'unstable' ? 'bg-red-100 text-red-800' : ''}
                      `}>
                        {report.recommendation}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full
                      ${report.status === 'completed' ? 'bg-green-100 text-green-800' : ''}
                      ${report.status === 'generating' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${report.status === 'calculating' ? 'bg-blue-100 text-blue-800' : ''}
                      ${report.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
                      ${report.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
                    `}>
                      {report.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(report.created_at).toLocaleString('ru-RU')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6">
        <Link
          href="/"
          className="inline-block px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          ← Вернуться к загрузке профилей
        </Link>
      </div>
    </div>
  )
}
