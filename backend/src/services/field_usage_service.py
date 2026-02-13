"""
Сервис анализа использования полей профиля в треке.

Анализирует track_data и generation_logs для определения,
какие поля StudentProfile были использованы на каких шагах B1-B8.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.models.generation_log import GenerationLog
from backend.src.models.personalized_track import PersonalizedTrack
from backend.src.schemas.track import FieldUsageItem, FieldUsageResponse


# Список всех полей StudentProfile с категориями важности
PROFILE_FIELDS = {
    # CRITICAL fields
    "topic": "CRITICAL",
    "subject_area": "CRITICAL",
    "experience_level": "CRITICAL",
    "desired_outcomes": "CRITICAL",
    "target_tasks": "CRITICAL",
    "task_hierarchy": "CRITICAL",
    "peak_task_id": "CRITICAL",
    "subtasks": "CRITICAL",
    "confusing_concepts": "CRITICAL",
    "diagnostic_result": "CRITICAL",
    "weekly_hours": "CRITICAL",
    "success_criteria": "CRITICAL",
    # IMPORTANT fields
    "key_barriers": "IMPORTANT",
    "mastery_signals": "IMPORTANT",
    "gaps_identified": "IMPORTANT",
    "misconceptions": "IMPORTANT",
    "schedule": "IMPORTANT",
    "practice_windows": "IMPORTANT",
    "preferred_formats": "IMPORTANT",
    "tech_access": "IMPORTANT",
    "motivation_level": "IMPORTANT",
    "support_available": "IMPORTANT",
    # OPTIONAL fields
    "prior_attempts": "OPTIONAL",
    "learning_style": "OPTIONAL",
    "accessibility_needs": "OPTIONAL",
    "language_preference": "OPTIONAL",
    "timezone": "OPTIONAL",
}


async def get_field_usage(track_id: UUID, db: AsyncSession) -> FieldUsageResponse:
    """
    Анализирует использование полей профиля в треке.

    Проверяет:
    1. generation_logs - какие поля упоминаются в step_output каждого шага
    2. track_data - какие поля из профиля вошли в финальный трек

    Args:
        track_id: ID трека для анализа
        db: Сессия базы данных

    Returns:
        FieldUsageResponse с информацией об использованных/неиспользованных полях

    Raises:
        ValueError: если трек не найден
    """
    # Загрузить трек
    track_result = await db.execute(
        select(PersonalizedTrack).where(PersonalizedTrack.id == track_id)
    )
    track = track_result.scalar_one_or_none()

    if not track:
        raise ValueError(f"Track {track_id} not found")

    # Загрузить логи генерации
    logs_result = await db.execute(
        select(GenerationLog)
        .where(GenerationLog.track_id == track_id)
        .order_by(GenerationLog.created_at)
    )
    logs = logs_result.scalars().all()

    # Анализ использования полей
    field_usage: dict[str, FieldUsageItem] = {}

    for field_name, criticality in PROFILE_FIELDS.items():
        used = False
        steps_used = []

        # Проверить использование в логах генерации
        for log in logs:
            if log.step_output and _field_mentioned_in_output(field_name, log.step_output):
                used = True
                steps_used.append(log.step_name)

        # Проверить наличие в финальном треке
        if track.track_data and _field_mentioned_in_output(field_name, track.track_data):
            used = True
            if "final_track" not in steps_used:
                steps_used.append("final_track")

        field_usage[field_name] = FieldUsageItem(
            field_name=field_name,
            used=used,
            steps=steps_used,
            criticality=criticality,
        )

    # Подсчёт статистики
    used_fields = [f for f in field_usage.values() if f.used]
    unused_fields = [f for f in field_usage.values() if not f.used]

    critical_unused = [
        f for f in unused_fields if PROFILE_FIELDS.get(f.field_name) == "CRITICAL"
    ]
    important_unused = [
        f for f in unused_fields if PROFILE_FIELDS.get(f.field_name) == "IMPORTANT"
    ]

    return FieldUsageResponse(
        track_id=track_id,
        used_fields=used_fields,
        unused_fields=unused_fields,
        total_fields=len(PROFILE_FIELDS),
        used_count=len(used_fields),
        unused_count=len(unused_fields),
        critical_unused_count=len(critical_unused),
        important_unused_count=len(important_unused),
    )


def _field_mentioned_in_output(field_name: str, output_data: dict) -> bool:
    """
    Проверяет, упоминается ли поле в выходных данных.

    Рекурсивно проходит по словарю и проверяет наличие ключа.

    Args:
        field_name: Название поля для поиска
        output_data: Словарь с данными для проверки

    Returns:
        True если поле найдено, иначе False
    """
    if not isinstance(output_data, dict):
        return False

    if field_name in output_data:
        return True

    # Рекурсивная проверка вложенных словарей
    for value in output_data.values():
        if isinstance(value, dict):
            if _field_mentioned_in_output(field_name, value):
                return True
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and _field_mentioned_in_output(field_name, item):
                    return True

    return False
