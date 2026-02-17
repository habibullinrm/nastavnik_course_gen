"""Сервис ручного режима отладки — CRUD сессий, оркестрация шагов."""

import logging
import uuid
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.src.core.config import settings
from backend.src.models.manual_session import ManualSession
from backend.src.models.manual_step_run import ManualStepRun
from backend.src.models.processor_config import ProcessorConfig
from backend.src.models.student_profile import StudentProfile

logger = logging.getLogger(__name__)

ML_URL = settings.ML_SERVICE_URL

# Маппинг зависимостей между шагами (auto-input)
STEP_DEPENDENCIES: dict[str, list[str]] = {
    "B1_validate": [],
    "B2_competencies": ["B1_validate"],
    "B3_ksa_matrix": ["B2_competencies"],
    "B4_learning_units": ["B3_ksa_matrix"],
    "B5_hierarchy": ["B4_learning_units", "B1_validate"],
    "B6_problem_formulations": ["B4_learning_units"],
    "B7_schedule": ["B5_hierarchy", "B6_problem_formulations"],
    "B8_validation": [
        "B1_validate", "B2_competencies", "B3_ksa_matrix",
        "B4_learning_units", "B5_hierarchy", "B6_problem_formulations",
        "B7_schedule",
    ],
}

ALL_STEPS = [
    "B1_validate", "B2_competencies", "B3_ksa_matrix", "B4_learning_units",
    "B5_hierarchy", "B6_problem_formulations", "B7_schedule", "B8_validation",
]


# ============================================================================
# Sessions CRUD
# ============================================================================


async def create_session(
    profile_id: uuid.UUID,
    name: str,
    description: str | None,
    db: AsyncSession,
) -> ManualSession:
    """Создать новую сессию отладки."""
    # Загрузить профиль
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

    session = ManualSession(
        id=uuid.uuid4(),
        profile_id=profile_id,
        profile_snapshot=profile.data,
        name=name,
        description=description,
        status="active",
    )
    db.add(session)
    await db.flush()
    return session


async def get_session(session_id: uuid.UUID, db: AsyncSession) -> ManualSession | None:
    """Получить сессию по ID."""
    result = await db.execute(
        select(ManualSession).where(ManualSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def list_sessions(
    db: AsyncSession,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[ManualSession], int]:
    """Список сессий с пагинацией."""
    query = select(ManualSession)
    count_query = select(func.count()).select_from(ManualSession)

    if status:
        query = query.where(ManualSession.status == status)
        count_query = count_query.where(ManualSession.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(ManualSession.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    sessions = list(result.scalars().all())
    return sessions, total


async def update_session(
    session_id: uuid.UUID,
    db: AsyncSession,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    profile_snapshot: dict | None = None,
) -> ManualSession:
    """Обновить сессию."""
    session = await get_session(session_id, db)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    if name is not None:
        session.name = name
    if description is not None:
        session.description = description
    if status is not None:
        session.status = status
    if profile_snapshot is not None:
        session.profile_snapshot = profile_snapshot
    session.updated_at = datetime.utcnow()

    await db.flush()
    return session


async def delete_session(session_id: uuid.UUID, db: AsyncSession) -> None:
    """Удалить сессию с каскадом."""
    session = await get_session(session_id, db)
    if not session:
        raise ValueError(f"Session {session_id} not found")
    await db.delete(session)
    await db.flush()


# ============================================================================
# Step Runs
# ============================================================================


async def get_step_status(
    session_id: uuid.UUID, db: AsyncSession
) -> dict[str, dict[str, Any]]:
    """Статус всех шагов в сессии."""
    result = await db.execute(
        select(ManualStepRun)
        .where(ManualStepRun.session_id == session_id)
        .order_by(ManualStepRun.step_name, ManualStepRun.run_number)
    )
    runs = result.scalars().all()

    steps = {}
    for step_name in ALL_STEPS:
        step_runs = [r for r in runs if r.step_name == step_name]
        last_run = step_runs[-1] if step_runs else None
        steps[step_name] = {
            "run_count": len(step_runs),
            "status": last_run.status if last_run else "pending",
            "last_run_id": str(last_run.id) if last_run else None,
            "last_rating": last_run.user_rating if last_run else None,
        }
    return steps


async def get_step_runs(
    session_id: uuid.UUID, step_name: str, db: AsyncSession
) -> list[ManualStepRun]:
    """История запусков шага."""
    result = await db.execute(
        select(ManualStepRun)
        .where(
            ManualStepRun.session_id == session_id,
            ManualStepRun.step_name == step_name,
        )
        .order_by(ManualStepRun.run_number.desc())
    )
    return list(result.scalars().all())


async def get_run_by_id(
    run_id: uuid.UUID, db: AsyncSession
) -> ManualStepRun | None:
    """Получить запуск по ID."""
    result = await db.execute(
        select(ManualStepRun).where(ManualStepRun.id == run_id)
    )
    return result.scalar_one_or_none()


async def _get_auto_input(
    session_id: uuid.UUID, step_name: str, profile_snapshot: dict, db: AsyncSession
) -> dict[str, Any]:
    """Вычислить входные данные шага из предыдущих результатов."""
    deps = STEP_DEPENDENCIES.get(step_name, [])
    if not deps:
        return profile_snapshot

    input_data: dict[str, Any] = {"profile": profile_snapshot}

    for dep_step in deps:
        result = await db.execute(
            select(ManualStepRun)
            .where(
                ManualStepRun.session_id == session_id,
                ManualStepRun.step_name == dep_step,
                ManualStepRun.status == "completed",
            )
            .order_by(ManualStepRun.run_number.desc())
            .limit(1)
        )
        dep_run = result.scalar_one_or_none()
        if dep_run and dep_run.parsed_result:
            input_data[dep_step] = dep_run.parsed_result

    return input_data


async def run_step(
    session_id: uuid.UUID,
    step_name: str,
    db: AsyncSession,
    prompt_version_id: uuid.UUID | None = None,
    custom_prompt: str | None = None,
    input_data: dict[str, Any] | None = None,
    llm_params: dict[str, Any] | None = None,
    run_preprocessors: bool = True,
    run_postprocessors: bool = True,
    use_mock: bool = True,
) -> ManualStepRun:
    """Запустить шаг — главная функция оркестрации."""
    session = await get_session(session_id, db)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    # Определить номер запуска
    count_result = await db.execute(
        select(func.count())
        .select_from(ManualStepRun)
        .where(
            ManualStepRun.session_id == session_id,
            ManualStepRun.step_name == step_name,
        )
    )
    run_number = (count_result.scalar() or 0) + 1

    # Определить промпт
    prompt_text = custom_prompt
    if not prompt_text and prompt_version_id:
        from backend.src.services.prompt_service import get_version_by_id
        pv = await get_version_by_id(prompt_version_id, db)
        if pv:
            prompt_text = pv.prompt_text

    if not prompt_text:
        # Загрузить baseline промпт из ML
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{ML_URL}/manual/render-prompt",
                json={"step_name": step_name, "profile": session.profile_snapshot},
            )
            resp.raise_for_status()
            render_data = resp.json()
            prompt_text = render_data["rendered_prompt"]

    # Определить входные данные
    if input_data is None:
        input_data = await _get_auto_input(
            session_id, step_name, session.profile_snapshot, db
        )

    # Создать запись запуска
    step_run = ManualStepRun(
        id=uuid.uuid4(),
        session_id=session_id,
        step_name=step_name,
        run_number=run_number,
        prompt_version_id=prompt_version_id,
        rendered_prompt=prompt_text,
        input_data=input_data,
        llm_params=llm_params or {"temperature": 0.3, "max_tokens": 8000},
        status="running",
    )
    db.add(step_run)
    await db.flush()

    try:
        # Пре-процессоры
        preprocessor_results = []
        if run_preprocessors:
            preprocessor_results = await _run_processors(
                session_id, step_name, "pre", input_data, db
            )
            step_run.preprocessor_results = preprocessor_results

        # Выполнить шаг через ML
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{ML_URL}/manual/execute-step",
                json={
                    "step_name": step_name,
                    "prompt": prompt_text,
                    "input_data": input_data,
                    "llm_params": step_run.llm_params,
                    "use_mock": use_mock,
                },
            )
            resp.raise_for_status()
            exec_result = resp.json()

        step_run.raw_response = exec_result.get("raw_response")
        step_run.parsed_result = exec_result.get("parsed_result")
        step_run.parse_error = exec_result.get("parse_error")
        step_run.tokens_used = exec_result.get("tokens_used", 0)
        step_run.duration_ms = exec_result.get("duration_ms", 0)

        # Пост-процессоры
        if run_postprocessors and step_run.parsed_result:
            postprocessor_results = await _run_processors(
                session_id, step_name, "post", step_run.parsed_result, db
            )
            step_run.postprocessor_results = postprocessor_results

        # Авто-метрики
        if step_run.parsed_result:
            from backend.src.services.evaluation_service import compute_auto_evaluation
            step_run.auto_evaluation = await compute_auto_evaluation(
                step_name, step_run.parsed_result, input_data
            )

        step_run.status = "completed" if not step_run.parse_error else "failed"

    except Exception as e:
        logger.error(f"Step {step_name} run failed: {e}")
        step_run.status = "failed"
        step_run.parse_error = str(e)

    await db.flush()
    return step_run


async def update_run_rating(
    run_id: uuid.UUID,
    user_rating: int | None,
    user_notes: str | None,
    db: AsyncSession,
) -> ManualStepRun:
    """Обновить рейтинг и заметки запуска."""
    run = await get_run_by_id(run_id, db)
    if not run:
        raise ValueError(f"Run {run_id} not found")

    if user_rating is not None:
        run.user_rating = user_rating
    if user_notes is not None:
        run.user_notes = user_notes

    await db.flush()
    return run


# ============================================================================
# Processors
# ============================================================================


async def _run_processors(
    session_id: uuid.UUID,
    step_name: str,
    processor_type: str,
    data: dict[str, Any],
    db: AsyncSession,
) -> list[dict[str, Any]]:
    """Запустить процессоры указанного типа для шага."""
    result = await db.execute(
        select(ProcessorConfig)
        .where(
            ProcessorConfig.session_id == session_id,
            ProcessorConfig.step_name == step_name,
            ProcessorConfig.processor_type == processor_type,
            ProcessorConfig.enabled == True,
        )
        .order_by(ProcessorConfig.execution_order)
    )
    configs = result.scalars().all()

    results = []
    for config in configs:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{ML_URL}/manual/processors/run",
                    json={
                        "processor_name": config.processor_name,
                        "data": data,
                        "step_name": step_name,
                        "config_params": config.config_params,
                    },
                )
                resp.raise_for_status()
                results.append(resp.json())
        except Exception as e:
            results.append({
                "name": config.processor_name,
                "passed": False,
                "error": str(e),
            })

    return results


async def get_processor_configs(
    session_id: uuid.UUID, step_name: str, db: AsyncSession
) -> list[ProcessorConfig]:
    """Получить конфиги процессоров для шага."""
    result = await db.execute(
        select(ProcessorConfig)
        .where(
            ProcessorConfig.session_id == session_id,
            ProcessorConfig.step_name == step_name,
        )
        .order_by(ProcessorConfig.execution_order)
    )
    return list(result.scalars().all())


async def set_processor_configs(
    session_id: uuid.UUID,
    step_name: str,
    processors: list[dict[str, Any]],
    db: AsyncSession,
) -> list[ProcessorConfig]:
    """Задать конфиги процессоров для шага (полная замена)."""
    # Удалить старые
    await db.execute(
        delete(ProcessorConfig).where(
            ProcessorConfig.session_id == session_id,
            ProcessorConfig.step_name == step_name,
        )
    )

    # Создать новые
    configs = []
    for p in processors:
        config = ProcessorConfig(
            id=uuid.uuid4(),
            session_id=session_id,
            step_name=step_name,
            processor_type=p["processor_type"],
            processor_name=p["processor_name"],
            execution_order=p.get("execution_order", 0),
            enabled=p.get("enabled", True),
            config_params=p.get("config_params"),
        )
        db.add(config)
        configs.append(config)

    await db.flush()
    return configs
