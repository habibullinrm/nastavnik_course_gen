"""Service for managing student profiles."""

import json
import uuid
from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.student_profile import StudentProfile
from backend.src.schemas.student_profile import StudentProfileInput, ValidationResult


async def upload_and_validate(
    db: AsyncSession, filename: str, file_content: bytes
) -> tuple[StudentProfile, ValidationResult]:
    """
    Upload and validate a student profile JSON.

    Args:
        db: Database session
        filename: Original filename
        file_content: JSON file content as bytes

    Returns:
        Tuple of (created profile, validation result)
    """
    # Parse JSON
    try:
        profile_data = json.loads(file_content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        # Return invalid profile with error
        validation_result = ValidationResult(
            valid=False, errors=[f"Invalid JSON: {str(e)}"], warnings=[]
        )
        # Save anyway for inspection
        profile = StudentProfile(
            id=uuid.uuid4(),
            data={"error": "invalid_json"},
            filename=filename,
            validation_result=validation_result.model_dump(),
            topic="<parsing error>",
            experience_level=None,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile, validation_result

    # Validate against Pydantic schema
    errors: list[str] = []
    warnings: list[str] = []

    try:
        validated = StudentProfileInput.model_validate(profile_data)

        # Check IMPORTANT fields for warnings
        if not validated.schedule:
            warnings.append("IMPORTANT field 'schedule' is missing")
        if not validated.practice_windows:
            warnings.append("IMPORTANT field 'practice_windows' is missing")
        if not validated.preferred_formats:
            warnings.append("IMPORTANT field 'preferred_formats' is missing")
        if not validated.tech_access:
            warnings.append("IMPORTANT field 'tech_access' is missing")
        if not validated.motivation_level:
            warnings.append("IMPORTANT field 'motivation_level' is missing")
        if not validated.support_available:
            warnings.append("IMPORTANT field 'support_available' is missing")

        valid = True

    except ValidationError as e:
        valid = False
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")

    validation_result = ValidationResult(valid=valid, errors=errors, warnings=warnings)

    # Extract topic and experience_level for easy querying
    topic = profile_data.get("topic", "<no topic>")
    experience_level = profile_data.get("experience_level")

    # Create profile record
    profile = StudentProfile(
        id=uuid.uuid4(),
        data=profile_data,
        filename=filename,
        validation_result=validation_result.model_dump(),
        topic=topic,
        experience_level=experience_level,
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return profile, validation_result


async def get_profile(db: AsyncSession, profile_id: uuid.UUID) -> StudentProfile | None:
    """Get a profile by ID."""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == profile_id)
    )
    return result.scalar_one_or_none()


async def list_profiles(db: AsyncSession, limit: int = 100) -> list[StudentProfile]:
    """List all profiles."""
    result = await db.execute(
        select(StudentProfile).order_by(StudentProfile.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
