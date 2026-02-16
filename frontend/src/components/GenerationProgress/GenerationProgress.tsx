/**
 * Компонент отображения прогресса генерации трека.
 *
 * Функции:
 * - Подключение к SSE /api/tracks/{id}/progress
 * - Пошаговый прогресс B1-B8 с временем, токенами, summary
 * - Кнопка "Остановить генерацию"
 * - Итоговые метрики
 */

'use client';

import { useEffect, useState, useCallback } from 'react';
import { cancelTrack } from '@/services/api';
import type { SSEStepUpdate, SSECompleteEvent, SSECancelledEvent, SSEErrorEvent } from '@/types';
import { STEP_DESCRIPTIONS } from '@/types';

interface StepState {
  step: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  description: string;
  duration_sec?: number;
  tokens_used?: number;
  summary?: Record<string, unknown>;
}

interface GenerationProgressProps {
  trackId: string;
  onComplete?: () => void;
}

const STEPS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'];

function formatDuration(sec: number): string {
  if (sec < 60) return `${sec.toFixed(1)}с`;
  const min = Math.floor(sec / 60);
  const rest = sec % 60;
  return `${min}м ${rest.toFixed(0)}с`;
}

function formatTokens(tokens: number): string {
  if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}k`;
  return String(tokens);
}

function SummaryBadges({ summary }: { summary: Record<string, unknown> }) {
  const entries = Object.entries(summary).filter(([, v]) => v != null);
  if (entries.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {entries.map(([key, value]) => (
        <span key={key} className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded">
          {key.replace(/_/g, ' ')}: {String(value)}
        </span>
      ))}
    </div>
  );
}

export default function GenerationProgress({ trackId, onComplete }: GenerationProgressProps) {
  const [steps, setSteps] = useState<StepState[]>(
    STEPS.map(step => ({
      step,
      status: 'pending',
      description: STEP_DESCRIPTIONS[step] || step,
    }))
  );
  const [error, setError] = useState<string | null>(null);
  const [failedStep, setFailedStep] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const [cancelled, setCancelled] = useState(false);
  const [cancelledSteps, setCancelledSteps] = useState<string[]>([]);
  const [totalDuration, setTotalDuration] = useState<number | null>(null);
  const [totalTokens, setTotalTokens] = useState<number | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${apiUrl}/api/tracks/${trackId}/progress`);

    const handleEvent = (eventType: string, data: string) => {
      try {
        const parsed = JSON.parse(data);

        if (eventType === 'step_update') {
          const update = parsed as SSEStepUpdate;
          setSteps(prev =>
            prev.map(s =>
              s.step === update.step
                ? {
                    ...s,
                    status: update.status,
                    description: update.description || s.description,
                    duration_sec: update.duration_sec ?? s.duration_sec,
                    tokens_used: update.tokens_used ?? s.tokens_used,
                    summary: update.summary ?? s.summary,
                  }
                : s
            )
          );
        } else if (eventType === 'complete') {
          const event = parsed as SSECompleteEvent;
          setCompleted(true);
          setTotalDuration(event.total_duration_sec);
          setTotalTokens(event.total_tokens);
          eventSource.close();
          if (onComplete) onComplete();
        } else if (eventType === 'cancelled') {
          const event = parsed as SSECancelledEvent;
          setCancelled(true);
          setCancelledSteps(event.completed_steps);
          eventSource.close();
        } else if (eventType === 'error') {
          const event = parsed as SSEErrorEvent;
          setError(event.error);
          setFailedStep(event.failed_step || null);
          eventSource.close();
        }
      } catch {
        // Ignore parse errors
      }
    };

    // Listen for named events
    eventSource.addEventListener('step_update', (e) => handleEvent('step_update', e.data));
    eventSource.addEventListener('complete', (e) => handleEvent('complete', e.data));
    eventSource.addEventListener('cancelled', (e) => handleEvent('cancelled', e.data));
    eventSource.addEventListener('error', (e) => {
      if (e.data) {
        handleEvent('error', e.data);
      }
    });

    let errorCount = 0;
    eventSource.onerror = () => {
      errorCount++;
      // Close after too many reconnect failures
      if (errorCount > 10) {
        eventSource.close();
      }
    };

    return () => eventSource.close();
  }, [trackId, onComplete]);

  const handleCancel = useCallback(async () => {
    setCancelling(true);
    try {
      await cancelTrack(trackId);
    } catch {
      // Ignore cancel errors
    }
  }, [trackId]);

  const completedCount = steps.filter(s => s.status === 'completed').length;
  const progress = (completedCount / STEPS.length) * 100;

  // Fallback: если все 8 шагов completed, но SSE complete event не дошёл
  useEffect(() => {
    if (completedCount === STEPS.length && !completed && !cancelled && !error) {
      setCompleted(true);
      if (onComplete) onComplete();
    }
  }, [completedCount, completed, cancelled, error, onComplete]);

  const isRunning = !completed && !cancelled && !error;
  const currentStep = Math.min(completedCount + 1, STEPS.length);

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">Генерация трека</h2>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className={`h-4 rounded-full transition-all duration-500 ${
            error ? 'bg-red-500' : cancelled ? 'bg-yellow-500' : 'bg-blue-600'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-center text-gray-600">
        {completed && 'Генерация завершена'}
        {cancelled && `Остановлено (${cancelledSteps.length}/8 шагов)`}
        {error && 'Ошибка генерации'}
        {isRunning && `Шаг ${currentStep}/8 (${Math.round(progress)}%)`}
      </p>

      {/* Step Logs */}
      <div className="space-y-2">
        {steps.map((s) => (
          <div
            key={s.step}
            className={`p-3 rounded-lg border ${
              s.status === 'completed'
                ? 'bg-green-50 border-green-200'
                : s.status === 'running'
                ? 'bg-blue-50 border-blue-200'
                : s.status === 'failed'
                ? 'bg-red-50 border-red-200'
                : 'bg-gray-50 border-gray-200'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-lg">
                  {s.status === 'completed' && '\u2713'}
                  {s.status === 'running' && '\u23F3'}
                  {s.status === 'failed' && '\u2717'}
                  {s.status === 'pending' && '\u25CB'}
                </span>
                <div>
                  <span className="font-semibold">{s.step}</span>
                  <span className="text-sm text-gray-500 ml-2">{s.description}</span>
                </div>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                {s.duration_sec != null && (
                  <span title="Время">{formatDuration(s.duration_sec)}</span>
                )}
                {s.tokens_used != null && s.tokens_used > 0 && (
                  <span title="Токены" className="text-gray-400">
                    {formatTokens(s.tokens_used)} tok
                  </span>
                )}
              </div>
            </div>
            {s.summary && <SummaryBadges summary={s.summary} />}
          </div>
        ))}
      </div>

      {/* Cancel Button */}
      {isRunning && (
        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {cancelling ? 'Останавливаем...' : 'Остановить генерацию'}
        </button>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Ошибка{failedStep ? ` на шаге ${failedStep}` : ''}</p>
          <p>{error}</p>
        </div>
      )}

      {/* Cancelled */}
      {cancelled && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <p className="font-bold">Генерация остановлена</p>
          <p>Завершённые шаги: {cancelledSteps.join(', ') || 'нет'}</p>
        </div>
      )}

      {/* Total Metrics */}
      {completed && totalDuration != null && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-1">
          <p className="font-bold text-green-800">Генерация завершена</p>
          <div className="flex gap-6 text-sm text-green-700">
            <span>Время: {formatDuration(totalDuration)}</span>
            {totalTokens != null && <span>Токены: {formatTokens(totalTokens)}</span>}
          </div>
        </div>
      )}

      {/* View Result Button */}
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
