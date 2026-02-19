"""API endpoints for student profiles."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db
from backend.src.models.personalized_track import PersonalizedTrack
from backend.src.schemas.student_profile import (
    LastTrackResponse,
    ProfileDetail,
    ProfileFormResponse,
    ProfileSummary,
    ProfileUploadResponse,
)
from backend.src.services import profile_service

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfileUploadResponse)
async def upload_profile(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and validate a student profile JSON.

    Returns validation result with errors/warnings.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    # Read file content
    content = await file.read()

    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    # Upload and validate
    profile, validation_result = await profile_service.upload_and_validate(
        db, file.filename, content
    )

    return ProfileUploadResponse(
        id=profile.id,
        filename=profile.filename,
        topic=profile.topic,
        experience_level=profile.experience_level,
        validation_result=validation_result,
        created_at=profile.created_at,
    )


@router.get("", response_model=dict)
async def list_profiles(
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded profiles."""
    profiles = await profile_service.list_profiles(db)

    return {
        "profiles": [
            ProfileSummary(
                id=p.id,
                filename=p.filename,
                topic=p.topic,
                profile_name=p.data.get("profile_name") if isinstance(p.data, dict) else None,
                experience_level=p.experience_level,
                created_at=p.created_at,
            )
            for p in profiles
        ]
    }




@router.post("/form", response_model=ProfileFormResponse, status_code=201)
async def create_profile_from_form(
    profile_data: Annotated[dict[str, Any], Body()],
    db: AsyncSession = Depends(get_db),
):
    """Создание профиля из данных формы (JSON body, без загрузки файла)."""
    if not profile_data.get("topic"):
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "topic"], "msg": "field required", "type": "value_error.missing"}],
        )

    profile, validation_result = await profile_service.create_from_form(db, profile_data)

    return ProfileFormResponse(
        id=profile.id,
        topic=profile.topic,
        experience_level=profile.experience_level,
        validation_result=validation_result,
        created_at=profile.created_at,
    )


@router.put("/{profile_id}", response_model=ProfileFormResponse)
async def update_profile(
    profile_id: UUID,
    profile_data: Annotated[dict[str, Any], Body()],
    db: AsyncSession = Depends(get_db),
):
    """Обновление существующего профиля (полная замена data)."""
    try:
        profile, validation_result = await profile_service.update_profile(db, profile_id, profile_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Профиль не найден")

    return ProfileFormResponse(
        id=profile.id,
        topic=profile.topic,
        experience_level=profile.experience_level,
        validation_result=validation_result,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )

@router.get("/{profile_id}/last-track", response_model=LastTrackResponse)
async def get_last_track(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает краткую информацию о последнем треке профиля."""
    result = await db.execute(
        select(PersonalizedTrack)
        .where(PersonalizedTrack.profile_id == profile_id)
        .order_by(PersonalizedTrack.created_at.desc())
        .limit(1)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Для этого профиля треки не найдены")

    return LastTrackResponse(
        track_id=track.id,
        status=track.status,
        created_at=track.created_at,
    )


@router.get("/{profile_id}", response_model=ProfileDetail)
async def get_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific profile by ID."""
    profile = await profile_service.get_profile(db, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return ProfileDetail(
        id=profile.id,
        filename=profile.filename,
        topic=profile.topic,
        experience_level=profile.experience_level,
        data=profile.data,
        validation_result=profile.validation_result,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
