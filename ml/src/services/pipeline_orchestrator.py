"""Pipeline orchestrator - coordinates B1-B8 execution."""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from ml.src.pipeline import (
    b1_validate,
    b2_competencies,
    b3_ksa_matrix,
    b4_learning_units,
    b5_hierarchy,
    b6_problem_formulations,
    b7_schedule,
    b8_validation,
)
from ml.src.schemas.pipeline import GenerationMetadata, StepLog
from ml.src.schemas.pipeline_steps import PersonalizedTrack
from ml.src.services.deepseek_client import get_deepseek_client
from ml.src.services.step_logger import get_step_logger

logger = logging.getLogger(__name__)

STEP_DESCRIPTIONS = {
    "B1": "Валидация и обогащение профиля",
    "B2": "Формулировка компетенций",
    "B3": "KSA-матрица (Знания-Умения-Навыки)",
    "B4": "Проектирование учебных единиц",
    "B5": "Иерархия и уровни",
    "B6": "Формулировки проблем (PBL)",
    "B7": "Сборка расписания",
    "B8": "Валидация трека",
}

# URL бэкенда для проверки статуса отмены
BACKEND_URL = "http://backend:8000"


class PipelineError(Exception):
    """Pipeline execution error."""

    def __init__(self, step: str, message: str, details: Any = None):
        self.step = step
        self.message = message
        self.details = details
        super().__init__(f"Pipeline error at {step}: {message}")


class PipelineCancelled(Exception):
    """Pipeline was cancelled by user."""

    def __init__(self, completed_steps: list[str]):
        self.completed_steps = completed_steps
        super().__init__(
            f"Pipeline cancelled after steps: {', '.join(completed_steps)}"
        )


def _log_start(track_id: UUID, step: str, step_num: int) -> None:
    desc = STEP_DESCRIPTIONS.get(step, step)
    msg = f"[{track_id}] ▶ [{step_num}/8] {step}: {desc} — начало"
    logger.info(msg)
    print(msg, flush=True)


def _log_done(track_id: UUID, step: str, step_num: int, duration: float, tokens: int) -> None:
    desc = STEP_DESCRIPTIONS.get(step, step)
    msg = f"[{track_id}] ✓ [{step_num}/8] {step}: {desc} — {duration:.1f}s, {tokens} tokens"
    logger.info(msg)
    print(msg, flush=True)


def _log_fail(track_id: UUID, step: str, step_num: int, error: Exception) -> None:
    desc = STEP_DESCRIPTIONS.get(step, step)
    msg = f"[{track_id}] ✗ [{step_num}/8] {step}: {desc} — ОШИБКА: {error}"
    logger.error(msg)
    print(msg, flush=True)


async def _check_cancelled(track_id: UUID) -> bool:
    """
    Проверяет статус трека через backend API.
    Если статус "cancelling" — возвращает True.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/tracks/{track_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("status") in ("cancelling", "cancelled")
    except Exception as e:
        logger.warning(f"Failed to check cancellation status for {track_id}: {e}")
    return False


async def run_pipeline(
    profile: dict[str, Any],
    track_id: UUID,
    algorithm_version: str = "v1.0.0",
) -> dict[str, Any]:
    """
    Run the complete B1-B8 pipeline.

    Между шагами проверяет отмену через backend API.

    Args:
        profile: Student profile (validated JSON)
        track_id: UUID for this track generation
        algorithm_version: Algorithm version identifier

    Returns:
        Complete PersonalizedTrack data with metadata

    Raises:
        PipelineError: If any step fails
        PipelineCancelled: If cancelled by user
    """
    start_time = time.time()
    started_at = datetime.utcnow().isoformat()

    deepseek_client = await get_deepseek_client()
    step_logger = await get_step_logger()

    steps_log: list[StepLog] = []
    total_tokens = 0
    completed_step_names: list[str] = []

    # Storage for intermediate results
    intermediate_results = {}

    topic = profile.get("topic", "unknown")
    print(f"\n{'='*70}", flush=True)
    print(f"[{track_id}] Pipeline B1-B8: генерация трека", flush=True)
    print(f"[{track_id}] Тема: {topic}", flush=True)
    print(f"{'='*70}", flush=True)

    # Define pipeline steps
    async def _run_b1():
        b1_result, b1_meta = await b1_validate.run_b1_validate(
            profile, deepseek_client
        )
        intermediate_results["validated_profile"] = b1_result.model_dump()
        return b1_result, b1_meta, [b1_meta]

    async def _run_b2():
        b2_result, b2_meta = await b2_competencies.run_b2_competencies(
            intermediate_results["validated_profile"], deepseek_client
        )
        intermediate_results["competency_set"] = b2_result.model_dump()
        return b2_result, b2_meta, [b2_meta]

    async def _run_b3():
        b3_result, b3_meta = await b3_ksa_matrix.run_b3_ksa_matrix(
            profile,
            intermediate_results["competency_set"],
            deepseek_client,
        )
        intermediate_results["ksa_matrix"] = b3_result.model_dump()
        return b3_result, b3_meta, [b3_meta]

    async def _run_b4():
        b4_result, b4_meta = await b4_learning_units.run_b4_learning_units(
            intermediate_results["ksa_matrix"], deepseek_client
        )
        intermediate_results["learning_units"] = b4_result.model_dump()
        return b4_result, b4_meta, [b4_meta]

    async def _run_b5():
        nonlocal b1_result_ref, b5_result_ref
        b5_result, b5_meta = await b5_hierarchy.run_b5_hierarchy(
            intermediate_results["learning_units"],
            b1_result_ref.total_time_budget_minutes,
            b1_result_ref.estimated_weeks,
            deepseek_client,
        )
        b5_result_ref = b5_result
        intermediate_results["hierarchy"] = b5_result.model_dump()
        return b5_result, b5_meta, [b5_meta]

    async def _run_b6():
        b6_result, b6_meta = await b6_problem_formulations.run_b6_problem_formulations(
            intermediate_results["learning_units"]["clusters"],
            intermediate_results["learning_units"],
            deepseek_client,
        )
        intermediate_results["lesson_blueprints"] = b6_result.model_dump()
        return b6_result, b6_meta, [b6_meta]

    async def _run_b7():
        b7_result, b7_meta = await b7_schedule.run_b7_schedule(
            intermediate_results["hierarchy"],
            intermediate_results["lesson_blueprints"],
            profile,
            b5_result_ref.total_weeks,
            deepseek_client,
        )
        intermediate_results["schedule"] = b7_result.model_dump()
        return b7_result, b7_meta, [b7_meta]

    async def _run_b8():
        complete_track_data = {
            "validated_profile": intermediate_results["validated_profile"],
            "competency_set": intermediate_results["competency_set"],
            "ksa_matrix": intermediate_results["ksa_matrix"],
            "learning_units": intermediate_results["learning_units"],
            "hierarchy": intermediate_results["hierarchy"],
            "lesson_blueprints": intermediate_results["lesson_blueprints"],
            "schedule": intermediate_results["schedule"],
        }
        b8_result, b8_meta = await b8_validation.run_b8_validation(
            complete_track_data, profile, deepseek_client
        )
        intermediate_results["validation"] = b8_result.model_dump()
        return b8_result, b8_meta, [b8_meta]

    # Refs needed across steps
    b1_result_ref = None
    b5_result_ref = None

    steps = [
        ("B1", "B1_validate", _run_b1),
        ("B2", "B2_competencies", _run_b2),
        ("B3", "B3_ksa_matrix", _run_b3),
        ("B4", "B4_learning_units", _run_b4),
        ("B5", "B5_hierarchy", _run_b5),
        ("B6", "B6_problem_formulations", _run_b6),
        ("B7", "B7_schedule", _run_b7),
        ("B8", "B8_validation", _run_b8),
    ]

    try:
        for step_num, (short_name, step_name, step_fn) in enumerate(steps, 1):
            # Проверить отмену перед каждым шагом
            if await _check_cancelled(track_id):
                print(f"[{track_id}] ⚠ Отмена обнаружена перед {short_name}", flush=True)
                raise PipelineCancelled(completed_step_names)

            _log_start(track_id, short_name, step_num)
            step_start = time.time()

            try:
                result, meta, llm_calls = await step_fn()
                step_duration = time.time() - step_start
                step_tokens = meta["tokens_used"]
                total_tokens += step_tokens

                # Save b1_result ref for b5
                if short_name == "B1":
                    b1_result_ref = result

                await step_logger.log_step(
                    track_id=track_id,
                    step_name=step_name,
                    step_output=result.model_dump() if hasattr(result, "model_dump") else result,
                    llm_calls=llm_calls,
                    duration_sec=step_duration,
                )

                steps_log.append(
                    StepLog(
                        step_name=step_name,
                        duration_sec=step_duration,
                        tokens_used=step_tokens,
                        success=True,
                    )
                )
                completed_step_names.append(short_name)
                _log_done(track_id, short_name, step_num, step_duration, step_tokens)

            except PipelineCancelled:
                raise
            except Exception as e:
                _log_fail(track_id, short_name, step_num, e)
                raise PipelineError(step_name, str(e))

        # =====================================================================
        # Assemble Final Track
        # =====================================================================
        finished_at = datetime.utcnow().isoformat()
        total_duration = time.time() - start_time

        metadata = GenerationMetadata(
            algorithm_version=algorithm_version,
            started_at=started_at,
            finished_at=finished_at,
            steps_log=steps_log,
            llm_calls_count=len(steps_log),
            total_tokens=total_tokens,
            total_duration_sec=total_duration,
        )

        track_data = {
            "validated_profile": intermediate_results["validated_profile"],
            "competency_set": intermediate_results["competency_set"],
            "ksa_matrix": intermediate_results["ksa_matrix"],
            "learning_units": intermediate_results["learning_units"],
            "hierarchy": intermediate_results["hierarchy"],
            "lesson_blueprints": intermediate_results["lesson_blueprints"],
            "schedule": intermediate_results["schedule"],
            "validation": intermediate_results["validation"],
        }

        print(f"\n{'='*70}", flush=True)
        print(
            f"[{track_id}] Pipeline ЗАВЕРШЁН: {total_duration:.1f}s, "
            f"{total_tokens} tokens, 8/8 шагов",
            flush=True,
        )
        print(f"{'='*70}\n", flush=True)

        return {
            "track_data": track_data,
            "generation_metadata": metadata.model_dump(),
            "validation_b8": intermediate_results["validation"],
            "algorithm_version": algorithm_version,
        }

    except PipelineCancelled as e:
        total_duration = time.time() - start_time
        print(
            f"\n[{track_id}] Pipeline ОТМЕНЁН после {total_duration:.1f}s, "
            f"{total_tokens} tokens, {len(completed_step_names)}/8 шагов",
            flush=True,
        )
        raise

    except PipelineError:
        total_duration = time.time() - start_time
        print(
            f"\n[{track_id}] Pipeline ПРЕРВАН после {total_duration:.1f}s, "
            f"{total_tokens} tokens, {len(steps_log)}/8 шагов завершено",
            flush=True,
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected pipeline error: {e}")
        raise PipelineError("unknown", f"Unexpected error: {e}")


async def run_pipeline_batch(
    profile: dict[str, Any],
    track_ids: list[UUID],
    algorithm_version: str = "v1.0.0",
) -> dict[str, Any]:
    """
    Run B1-B8 pipeline for N tracks (batch mode).

    Для каждого шага запускает N генераций параллельно (asyncio.gather),
    после каждого шага логирует результаты для всех треков.

    Args:
        profile: Student profile (validated JSON)
        track_ids: List of track UUIDs
        algorithm_version: Algorithm version identifier

    Returns:
        {"results": [result_per_track]}
    """
    batch_size = len(track_ids)
    results: list[dict[str, Any]] = [{} for _ in range(batch_size)]

    print(f"\n{'='*70}", flush=True)
    print(f"Batch pipeline: {batch_size} треков", flush=True)
    print(f"Track IDs: {[str(t) for t in track_ids]}", flush=True)
    print(f"{'='*70}", flush=True)

    # Запустить каждый pipeline параллельно через asyncio.gather
    async def _run_single(index: int, tid: UUID) -> dict[str, Any]:
        try:
            result = await run_pipeline(profile, tid, algorithm_version)
            return {"index": index, **result}
        except PipelineCancelled as e:
            return {"index": index, "status": "cancelled", "completed_steps": e.completed_steps}
        except PipelineError as e:
            return {"index": index, "status": "failed", "error": str(e)}
        except Exception as e:
            return {"index": index, "status": "failed", "error": str(e)}

    tasks = [_run_single(i, tid) for i, tid in enumerate(track_ids)]
    completed = await asyncio.gather(*tasks, return_exceptions=False)

    for res in completed:
        idx = res.pop("index", 0)
        results[idx] = res

    print(f"\n{'='*70}", flush=True)
    print(f"Batch pipeline ЗАВЕРШЁН: {batch_size} треков обработано", flush=True)
    print(f"{'='*70}\n", flush=True)

    return {"results": results}
