'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ProfileForm } from '@/components/ProfileForm'
import { createProfileFromForm } from '@/services/api'
import type { ProfileFormState } from '@/types'

export default function ProfileNewPage() {
  const router = useRouter()
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const handleSave = async (state: ProfileFormState) => {
    setSaving(true)
    setSaveError(null)
    try {
      const result = await createProfileFromForm(state)
      router.push(`/tracks/generate?profile_id=${result.id}`)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ошибка сохранения'
      setSaveError(message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-6">
          <a href="/profiles" className="text-blue-600 hover:underline text-sm">← Профили</a>
          <h1 className="text-2xl font-bold text-gray-900">Создать профиль</h1>
        </div>
        <ProfileForm
          onSave={handleSave}
          saving={saving}
          saveError={saveError}
        />
      </div>
    </main>
  )
}
