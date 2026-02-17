"""Сервис версионирования промптов."""

import logging
import uuid
from typing import Any

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.config import settings
from backend.src.models.prompt_version import PromptVersion

logger = logging.getLogger(__name__)

ML_URL = settings.ML_SERVICE_URL


async def get_all_steps_latest(db: AsyncSession) -> list[dict[str, Any]]:
    """Получить все шаги с последней версией промпта."""
    # Подзапрос: максимальная версия для каждого step_name
    subq = (
        select(
            PromptVersion.step_name,
            func.max(PromptVersion.version).label("max_version"),
        )
        .group_by(PromptVersion.step_name)
        .subquery()
    )

    result = await db.execute(
        select(PromptVersion)
        .join(
            subq,
            (PromptVersion.step_name == subq.c.step_name)
            & (PromptVersion.version == subq.c.max_version),
        )
        .order_by(PromptVersion.step_name)
    )
    versions = result.scalars().all()

    return [
        {
            "step_name": v.step_name,
            "latest_version": v.version,
            "latest_prompt_id": v.id,
            "is_baseline": v.is_baseline,
            "created_at": v.created_at,
        }
        for v in versions
    ]


async def get_step_versions(step_name: str, db: AsyncSession) -> list[PromptVersion]:
    """Все версии промпта для шага."""
    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.step_name == step_name)
        .order_by(PromptVersion.version.desc())
    )
    return list(result.scalars().all())


async def create_version(
    step_name: str,
    prompt_text: str,
    change_description: str | None,
    is_baseline: bool,
    db: AsyncSession,
) -> PromptVersion:
    """Создать новую версию промпта."""
    # Определить следующий номер версии
    result = await db.execute(
        select(func.coalesce(func.max(PromptVersion.version), 0))
        .where(PromptVersion.step_name == step_name)
    )
    max_version = result.scalar() or 0

    version = PromptVersion(
        id=uuid.uuid4(),
        step_name=step_name,
        version=max_version + 1,
        prompt_text=prompt_text,
        change_description=change_description,
        is_baseline=is_baseline,
    )
    db.add(version)
    await db.flush()
    return version


async def get_version_by_id(version_id: uuid.UUID, db: AsyncSession) -> PromptVersion | None:
    """Получить версию по ID."""
    result = await db.execute(
        select(PromptVersion).where(PromptVersion.id == version_id)
    )
    return result.scalar_one_or_none()


async def rollback_to_version(
    step_name: str, version: int, db: AsyncSession
) -> PromptVersion:
    """Откатить к указанной версии (создать новую версию с тем же текстом)."""
    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.step_name == step_name, PromptVersion.version == version)
    )
    old = result.scalar_one_or_none()
    if not old:
        raise ValueError(f"Version {version} not found for step {step_name}")

    return await create_version(
        step_name=step_name,
        prompt_text=old.prompt_text,
        change_description=f"Откат к версии {version}",
        is_baseline=False,
        db=db,
    )


async def load_baselines(db: AsyncSession) -> list[PromptVersion]:
    """Загрузить baseline промпты из ML-сервиса."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{ML_URL}/manual/prompts/baseline")
        response.raise_for_status()
        data = response.json()

    created = []
    for baseline in data["prompts"]:
        step_name = baseline["step_name"]
        prompt_text = baseline["prompt_text"]

        if prompt_text.startswith("ERROR:"):
            logger.warning(f"Skipping baseline for {step_name}: {prompt_text}")
            continue

        # Проверить, есть ли уже baseline для этого шага
        result = await db.execute(
            select(PromptVersion)
            .where(
                PromptVersion.step_name == step_name,
                PromptVersion.is_baseline == True,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Обновить существующий baseline
            existing.prompt_text = prompt_text
            created.append(existing)
        else:
            version = await create_version(
                step_name=step_name,
                prompt_text=prompt_text,
                change_description="Baseline из .py файлов",
                is_baseline=True,
                db=db,
            )
            created.append(version)

    await db.flush()
    return created
