/**
 * Страница прогресса генерации трека.
 *
 * Показывает real-time прогресс выполнения B1-B8.
 * После завершения перенаправляет на просмотр трека.
 */

'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';
import GenerationProgress from '@/components/GenerationProgress/GenerationProgress';
import { generateTrack } from '@/services/api';

function GeneratePageContent() {
  const searchParams = useSearchParams();
  const profileId = searchParams.get('profile_id');
  const [trackId, setTrackId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId) {
      setError('Profile ID not provided');
      return;
    }

    // Запустить генерацию
    generateTrack(profileId)
      .then(response => {
        setTrackId(response.track_id);
      })
      .catch(err => {
        setError(err instanceof Error ? err.message : 'Generation failed');
      });
  }, [profileId]);

  if (error) {
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

  if (!trackId) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto">
          <p className="text-center">Запуск генерации...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <GenerationProgress
        trackId={trackId}
        onComplete={() => {
          setTimeout(() => {
            window.location.href = `/tracks/${trackId}`;
          }, 1000);
        }}
      />
    </main>
  );
}

export default function GeneratePage() {
  return (
    <Suspense fallback={<div className="min-h-screen p-8"><div className="max-w-2xl mx-auto"><p className="text-center">Загрузка...</p></div></div>}>
      <GeneratePageContent />
    </Suspense>
  );
}
