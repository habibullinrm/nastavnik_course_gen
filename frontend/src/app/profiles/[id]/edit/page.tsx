'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { ProfileForm } from '@/components/ProfileForm'
import { getProfile, updateProfile } from '@/services/api'
import type { ProfileFormState } from '@/types'

export default function ProfileEditPage() {
  const router = useRouter()
  const params = useParams()
  const profileId = params?.id as string

  const [initialData, setInitialData] = useState<Partial<ProfileFormState> | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  useEffect(() => {
    if (!profileId) return
    setLoading(true)
    getProfile(profileId)
      .then(profile => {
        setInitialData(profile.data as Partial<ProfileFormState>)
      })
      .catch(err => {
        setLoadError(err instanceof Error ? err.message : 'Ошибка загрузки профиля')
      })
      .finally(() => setLoading(false))
  }, [profileId])

  const handleSave = async (state: ProfileFormState) => {
    setSaving(true)
    setSaveError(null)
    try {
      await updateProfile(profileId, state)
      router.push(`/tracks/generate?profile_id=${profileId}`)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ошибка сохранения'
      setSaveError(message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Загрузка профиля...</p>
      </main>
    )
  }

  if (loadError) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{loadError}</p>
          <a href="/profiles" className="text-blue-600 hover:underline">← К списку профилей</a>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-6">
          <a href="/profiles" className="text-blue-600 hover:underline text-sm">← Профили</a>
          <h1 className="text-2xl font-bold text-gray-900">Редактировать профиль</h1>
        </div>
        <ProfileForm
          initialData={initialData}
          profileId={profileId}
          onSave={handleSave}
          saving={saving}
          saveError={saveError}
        />
      </div>
    </main>
  )
}
