/**
 * Компонент загрузки JSON профиля студента.
 *
 * Функции:
 * - Drag-and-drop / file input для JSON файлов
 * - Отправка на POST /api/profiles
 * - Отображение validation результата (errors красным, warnings жёлтым)
 * - Кнопка "Сгенерировать трек" после успешной загрузки
 */

'use client';

import { useState } from 'react';
import { uploadProfile } from '@/services/api';
import type { ValidationResult } from '@/types';

interface ProfileUploadProps {
  onUploadSuccess?: (profileId: string) => void;
}

export default function ProfileUpload({ onUploadSuccess }: ProfileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setValidation(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await uploadProfile(file);

      setProfileId(response.id);
      setValidation(response.validation_result);

      if (response.validation_result.valid && onUploadSuccess) {
        onUploadSuccess(response.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold">Загрузка профиля студента</h2>

      {/* File Input */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer text-blue-600 hover:text-blue-800"
        >
          {file ? file.name : 'Выберите JSON файл или перетащите сюда'}
        </label>
      </div>

      {/* Upload Button */}
      {file && !profileId && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {uploading ? 'Загрузка...' : 'Загрузить профиль'}
        </button>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Validation Result */}
      {validation && (
        <div className="space-y-2">
          {validation.errors.length > 0 && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              <p className="font-bold">Ошибки:</p>
              <ul className="list-disc list-inside">
                {validation.errors.map((err, idx) => (
                  <li key={idx}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          {validation.warnings.length > 0 && (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
              <p className="font-bold">Предупреждения:</p>
              <ul className="list-disc list-inside">
                {validation.warnings.map((warn, idx) => (
                  <li key={idx}>{warn}</li>
                ))}
              </ul>
            </div>
          )}

          {validation.valid && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ✓ Профиль валиден
            </div>
          )}
        </div>
      )}

      {/* Generate Button */}
      {profileId && validation?.valid && (
        <button
          onClick={() => window.location.href = `/tracks/generate?profile_id=${profileId}`}
          className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
        >
          Сгенерировать трек
        </button>
      )}
    </div>
  );
}
