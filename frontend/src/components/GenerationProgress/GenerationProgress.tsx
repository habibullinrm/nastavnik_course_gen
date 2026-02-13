/**
 * Компонент отображения прогресса генерации трека.
 *
 * Функции:
 * - Подключение к SSE /api/tracks/{id}/progress
 * - Отображение текущего шага (B1...B8)
 * - Прогресс-бар
 * - Лог выполненных шагов
 */

'use client';

import { useEffect, useState } from 'react';

interface StepLog {
  step: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: number;
}

interface GenerationProgressProps {
  trackId: string;
  onComplete?: () => void;
}

const STEPS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'];

export default function GenerationProgress({ trackId, onComplete }: GenerationProgressProps) {
  const [currentStep, setCurrentStep] = useState<string>('B1');
  const [stepLogs, setStepLogs] = useState<StepLog[]>(
    STEPS.map(step => ({ step, status: 'pending' }))
  );
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/api/tracks/${trackId}/progress`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.status === 'completed') {
        setCompleted(true);
        eventSource.close();
        if (onComplete) {
          onComplete();
        }
      } else if (data.status === 'failed') {
        setError(data.error || 'Generation failed');
        eventSource.close();
      } else if (data.step) {
        setCurrentStep(data.step);
        setStepLogs(prev =>
          prev.map(log =>
            log.step === data.step
              ? { ...log, status: data.step_status, duration: data.duration }
              : log
          )
        );
      }
    };

    eventSource.onerror = () => {
      setError('Connection lost');
      eventSource.close();
    };

    return () => eventSource.close();
  }, [trackId, onComplete]);

  const progress = (stepLogs.filter(log => log.status === 'completed').length / STEPS.length) * 100;

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">Генерация трека</h2>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className="bg-blue-600 h-4 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-center text-gray-600">
        {completed ? 'Завершено' : `Шаг ${currentStep} (${Math.round(progress)}%)`}
      </p>

      {/* Step Logs */}
      <div className="space-y-2">
        {stepLogs.map((log) => (
          <div
            key={log.step}
            className={`p-3 rounded flex items-center justify-between ${
              log.status === 'completed'
                ? 'bg-green-100'
                : log.status === 'running'
                ? 'bg-blue-100'
                : log.status === 'failed'
                ? 'bg-red-100'
                : 'bg-gray-100'
            }`}
          >
            <span className="font-semibold">{log.step}</span>
            <span className="text-sm">
              {log.status === 'completed' && log.duration && `${log.duration}s`}
              {log.status === 'running' && '⏳'}
              {log.status === 'failed' && '✗'}
              {log.status === 'pending' && '○'}
            </span>
          </div>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Complete Button */}
      {completed && (
        <button
          onClick={() => window.location.href = `/tracks/${trackId}`}
          className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
        >
          Просмотреть результат
        </button>
      )}
    </div>
  );
}
