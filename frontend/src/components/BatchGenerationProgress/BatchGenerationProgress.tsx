/**
 * Компонент отображения прогресса batch-генерации.
 *
 * Функции:
 * - SSE подключение к /api/tracks/batch/{batchId}/progress
 * - Пошаговый прогресс для каждого из N треков
 * - Панель сравнения после завершения каждого шага для всех треков
 */

'use client';

import { useEffect, useState, useMemo } from 'react';
import type { SSEStepUpdate, SSEBatchCompleteEvent } from '@/types';
import { STEP_DESCRIPTIONS } from '@/types';

interface TrackStepState {
  step: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration_sec?: number;
  tokens_used?: number;
  summary?: Record<string, unknown>;
}

interface BatchGenerationProgressProps {
  batchId: string;
  trackIds: string[];
  onComplete?: () => void;
}

const STEPS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'];

// Ключевые метрики для сравнения по шагам
const COMPARISON_KEYS: Record<string, string[]> = {
  B1: ['effective_level', 'estimated_weeks'],
  B2: ['competencies_count'],
  B3: ['knowledge_count', 'skills_count', 'habits_count'],
  B4: ['units_count', 'clusters_count'],
  B5: ['total_weeks', 'levels'],
  B6: ['blueprints_count'],
  B7: ['weeks', 'checkpoints'],
  B8: ['overall_valid', 'checks'],
};

function formatDuration(sec: number): string {
  if (sec < 60) return `${sec.toFixed(1)}с`;
  const min = Math.floor(sec / 60);
  const rest = sec % 60;
  return `${min}м ${rest.toFixed(0)}с`;
}

function ComparisonTable({
  step,
  trackCount,
  trackSteps,
}: {
  step: string;
  trackCount: number;
  trackSteps: TrackStepState[][];
}) {
  const keys = COMPARISON_KEYS[step] || [];
  if (keys.length === 0) return null;

  const stepIndex = STEPS.indexOf(step);

  // Check if all tracks have completed this step
  const allCompleted = trackSteps.every(
    (ts) => ts[stepIndex]?.status === 'completed'
  );
  if (!allCompleted) return null;

  return (
    <div className="mt-2 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="text-left p-2 border">Метрика</th>
            {Array.from({ length: trackCount }, (_, i) => (
              <th key={i} className="text-center p-2 border">
                Трек {i + 1}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => {
            const values = trackSteps.map((ts) => {
              const summary = ts[stepIndex]?.summary;
              return summary?.[key] ?? '—';
            });

            // Highlight differences
            const allSame = values.every((v) => String(v) === String(values[0]));

            return (
              <tr key={key} className={allSame ? '' : 'bg-yellow-50'}>
                <td className="p-2 border text-gray-600">
                  {key.replace(/_/g, ' ')}
                </td>
                {values.map((val, i) => (
                  <td
                    key={i}
                    className={`p-2 border text-center ${
                      !allSame ? 'font-semibold' : ''
                    }`}
                  >
                    {String(val)}
                  </td>
                ))}
              </tr>
            );
          })}
          {/* Duration row */}
          <tr>
            <td className="p-2 border text-gray-600">Время</td>
            {trackSteps.map((ts, i) => (
              <td key={i} className="p-2 border text-center text-gray-500">
                {ts[stepIndex]?.duration_sec != null
                  ? formatDuration(ts[stepIndex].duration_sec!)
                  : '—'}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default function BatchGenerationProgress({
  batchId,
  trackIds,
  onComplete,
}: BatchGenerationProgressProps) {
  const trackCount = trackIds.length;

  // State: for each track, array of 8 step states
  const [trackSteps, setTrackSteps] = useState<TrackStepState[][]>(() =>
    Array.from({ length: trackCount }, () =>
      STEPS.map((step) => ({ step, status: 'pending' as const }))
    )
  );

  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [batchResults, setBatchResults] = useState<SSEBatchCompleteEvent['results'] | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    const eventSource = new EventSource(
      `${apiUrl}/api/tracks/batch/${batchId}/progress`
    );

    eventSource.addEventListener('step_update', (e) => {
      try {
        const update = JSON.parse(e.data) as SSEStepUpdate & { batch_index: number };
        const trackIndex = update.batch_index;
        const stepIndex = STEPS.indexOf(update.step);

        if (trackIndex >= 0 && stepIndex >= 0) {
          setTrackSteps((prev) => {
            const next = prev.map((ts) => ts.map((s) => ({ ...s })));
            next[trackIndex][stepIndex] = {
              step: update.step,
              status: update.status,
              duration_sec: update.duration_sec,
              tokens_used: update.tokens_used,
              summary: update.summary,
            };
            return next;
          });

          // Auto-expand comparison when all tracks complete a step
          setExpandedSteps((prev) => {
            const newSet = new Set(prev);
            newSet.add(update.step);
            return newSet;
          });
        }
      } catch {
        // ignore
      }
    });

    eventSource.addEventListener('batch_complete', (e) => {
      try {
        const data = JSON.parse(e.data) as SSEBatchCompleteEvent;
        setBatchResults(data.results);
        setCompleted(true);
        eventSource.close();
        if (onComplete) onComplete();
      } catch {
        // ignore
      }
    });

    eventSource.addEventListener('error', (e) => {
      if ((e as MessageEvent).data) {
        try {
          const data = JSON.parse((e as MessageEvent).data);
          setError(data.error || 'Unknown error');
        } catch {
          // ignore
        }
        eventSource.close();
      }
    });

    return () => eventSource.close();
  }, [batchId, onComplete, trackCount]);

  // Calculate overall progress
  const totalSteps = trackCount * STEPS.length;
  const completedSteps = trackSteps.reduce(
    (sum, ts) => sum + ts.filter((s) => s.status === 'completed').length,
    0
  );
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  // For each step, check if all tracks have completed it
  const stepCompletionStatus = useMemo(() => {
    return STEPS.map((_, stepIdx) => {
      const allDone = trackSteps.every(
        (ts) => ts[stepIdx]?.status === 'completed'
      );
      const anyRunning = trackSteps.some(
        (ts) => ts[stepIdx]?.status === 'running'
      );
      return { allDone, anyRunning };
    });
  }, [trackSteps]);

  const toggleStep = (step: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">
        Batch-генерация ({trackCount} треков)
      </h2>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className={`h-4 rounded-full transition-all duration-500 ${
            error ? 'bg-red-500' : 'bg-blue-600'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-center text-gray-600">
        {completed
          ? 'Все треки сгенерированы'
          : `${completedSteps}/${totalSteps} шагов (${Math.round(progress)}%)`}
      </p>

      {/* Steps with comparison */}
      <div className="space-y-3">
        {STEPS.map((step, stepIdx) => {
          const { allDone, anyRunning } = stepCompletionStatus[stepIdx];
          const isExpanded = expandedSteps.has(step);

          return (
            <div key={step} className="border rounded-lg overflow-hidden">
              {/* Step Header */}
              <button
                onClick={() => toggleStep(step)}
                className={`w-full p-3 flex items-center justify-between text-left ${
                  allDone
                    ? 'bg-green-50'
                    : anyRunning
                    ? 'bg-blue-50'
                    : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {allDone ? '\u2713' : anyRunning ? '\u23F3' : '\u25CB'}
                  </span>
                  <span className="font-semibold">{step}</span>
                  <span className="text-sm text-gray-500">
                    {STEP_DESCRIPTIONS[step]}
                  </span>
                </div>

                {/* Track progress indicators */}
                <div className="flex gap-1">
                  {trackSteps.map((ts, tIdx) => (
                    <span
                      key={tIdx}
                      className={`w-3 h-3 rounded-full ${
                        ts[stepIdx]?.status === 'completed'
                          ? 'bg-green-500'
                          : ts[stepIdx]?.status === 'running'
                          ? 'bg-blue-500 animate-pulse'
                          : ts[stepIdx]?.status === 'failed'
                          ? 'bg-red-500'
                          : 'bg-gray-300'
                      }`}
                      title={`Трек ${tIdx + 1}: ${ts[stepIdx]?.status}`}
                    />
                  ))}
                </div>
              </button>

              {/* Expanded: Comparison Table */}
              {isExpanded && (
                <div className="p-3 border-t">
                  <ComparisonTable
                    step={step}
                    trackCount={trackCount}
                    trackSteps={trackSteps}
                  />
                  {!allDone && (
                    <p className="text-sm text-gray-400 mt-2">
                      Ожидание завершения всех треков для сравнения...
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Batch Complete Summary */}
      {completed && batchResults && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="font-bold text-green-800 mb-2">
            Batch-генерация завершена
          </p>
          <div className="grid grid-cols-2 gap-2">
            {batchResults.map((r) => (
              <div
                key={r.track_id}
                className="flex items-center justify-between text-sm p-2 bg-white rounded border"
              >
                <span>Трек {r.batch_index + 1}</span>
                <span
                  className={
                    r.status === 'completed'
                      ? 'text-green-600'
                      : r.status === 'cancelled'
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }
                >
                  {r.status}
                  {r.duration_sec != null && ` (${formatDuration(r.duration_sec)})`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* View Tracks */}
      {completed && (
        <div className="flex gap-2">
          {trackIds.map((tid, i) => (
            <button
              key={tid}
              onClick={() => (window.location.href = `/tracks/${tid}`)}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 text-sm"
            >
              Трек {i + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
