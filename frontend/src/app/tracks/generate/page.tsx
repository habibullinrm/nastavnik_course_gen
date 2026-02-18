/**
 * Страница генерации трека.
 *
 * Режимы:
 * - Одиночная генерация: запуск 1 трека с real-time прогрессом
 * - Batch генерация: запуск N треков с пошаговым сравнением
 */

'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';
import GenerationProgress from '@/components/GenerationProgress/GenerationProgress';
import BatchGenerationProgress from '@/components/BatchGenerationProgress/BatchGenerationProgress';
import { generateTrack, generateTrackBatch } from '@/services/api';

type Mode = 'single' | 'batch';

function GeneratePageContent() {
  const searchParams = useSearchParams();
  const profileId = searchParams.get('profile_id');

  const [mode, setMode] = useState<Mode>('single');
  const [batchSize, setBatchSize] = useState(3);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Single mode state
  const [trackId, setTrackId] = useState<string | null>(null);

  // Batch mode state
  const [batchId, setBatchId] = useState<string | null>(null);
  const [trackIds, setTrackIds] = useState<string[]>([]);

  const handleStart = async () => {
    if (!profileId) {
      setError('Profile ID not provided');
      return;
    }

    setStarted(true);
    setError(null);

    try {
      if (mode === 'single') {
        const response = await generateTrack(profileId);
        setTrackId(response.track_id);
      } else {
        const response = await generateTrackBatch(profileId, batchSize);
        setBatchId(response.batch_id);
        setTrackIds(response.track_ids);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
      setStarted(false);
    }
  };

  // Auto-start for single mode if no batch params (backwards compatibility)
  useEffect(() => {
    if (profileId && !started && mode === 'single') {
      // Don't auto-start — let user choose mode
    }
  }, [profileId, started, mode]);

  if (error && !started) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </main>
    );
  }

  if (!profileId) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            Profile ID not provided. Add ?profile_id=... to URL.
          </div>
        </div>
      </main>
    );
  }

  // Show mode selection before starting
  if (!started) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">Генерация трека</h1>
            <a
              href={`/manual${profileId ? `?profile_id=${profileId}` : ''}`}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:border-gray-400 transition-colors"
            >
              🔧 Отладка промптов
            </a>
          </div>

          {/* Mode Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setMode('single')}
              className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors ${
                mode === 'single'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Одиночная</div>
              <div className="text-sm opacity-75">1 трек</div>
            </button>
            <button
              onClick={() => setMode('batch')}
              className={`flex-1 py-3 px-4 rounded-lg border-2 transition-colors ${
                mode === 'batch'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
              }`}
            >
              <div className="font-semibold">Batch</div>
              <div className="text-sm opacity-75">Сравнение N треков</div>
            </button>
          </div>

          {/* Batch Size Selector */}
          {mode === 'batch' && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Количество треков
              </label>
              <div className="flex gap-2">
                {[2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    onClick={() => setBatchSize(n)}
                    className={`w-12 h-12 rounded-lg border-2 font-bold ${
                      batchSize === n
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500">
                Больше треков = больше времени генерации, но точнее сравнение
              </p>
            </div>
          )}

          {/* Start Button */}
          <button
            onClick={handleStart}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 text-lg font-semibold"
          >
            {mode === 'single'
              ? 'Сгенерировать трек'
              : `Сгенерировать ${batchSize} треков`}
          </button>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>
      </main>
    );
  }

  // Single mode: show GenerationProgress
  if (mode === 'single' && trackId) {
    return (
      <main className="min-h-screen p-8">
        <GenerationProgress
          trackId={trackId}
          onComplete={() => {
            setTimeout(() => {
              window.location.href = `/tracks/${trackId}`;
            }, 2000);
          }}
        />
      </main>
    );
  }

  // Batch mode: show BatchGenerationProgress
  if (mode === 'batch' && batchId) {
    return (
      <main className="min-h-screen p-8">
        <BatchGenerationProgress
          batchId={batchId}
          trackIds={trackIds}
        />
      </main>
    );
  }

  // Loading state
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto">
        <p className="text-center">Запуск генерации...</p>
      </div>
    </main>
  );
}

export default function GeneratePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen p-8">
          <div className="max-w-2xl mx-auto">
            <p className="text-center">Загрузка...</p>
          </div>
        </div>
      }
    >
      <GeneratePageContent />
    </Suspense>
  );
}
