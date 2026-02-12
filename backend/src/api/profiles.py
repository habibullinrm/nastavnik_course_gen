"""API endpoints for student profiles."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db
from backend.src.schemas.student_profile import (
    ProfileDetail,
    ProfileSummary,
    ProfileUploadResponse,
)
from backend.src.services import profile_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


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
                experience_level=p.experience_level,
                created_at=p.created_at,
            )
            for p in profiles
        ]
    }


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
