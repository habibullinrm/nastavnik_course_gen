/**
 * Главная страница - загрузка JSON профиля студента.
 *
 * После успешной загрузки показывает кнопку генерации трека.
 */

import ProfileUpload from '@/components/ProfileUpload/ProfileUpload';

export default function HomePage() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">
          Сервис тестирования алгоритма генерации учебных треков
        </h1>
        <p className="text-gray-600 mb-8">
          Загрузите JSON профиль студента для запуска pipeline B1-B8
        </p>

        <ProfileUpload />
      </div>
    </main>
  );
}
