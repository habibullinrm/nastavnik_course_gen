"""Pipeline orchestrator - coordinates B1-B8 execution."""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any
from uuid import UUID

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


class PipelineError(Exception):
    """Pipeline execution error."""

    def __init__(self, step: str, message: str, details: Any = None):
        self.step = step
        self.message = message
        self.details = details
        super().__init__(f"Pipeline error at {step}: {message}")


async def run_pipeline(
    profile: dict[str, Any],
    track_id: UUID,
    algorithm_version: str = "v1.0.0",
) -> dict[str, Any]:
    """
    Run the complete B1-B8 pipeline.

    Args:
        profile: Student profile (validated JSON)
        track_id: UUID for this track generation
        algorithm_version: Algorithm version identifier

    Returns:
        Complete PersonalizedTrack data with metadata

    Raises:
        PipelineError: If any step fails
    """
    start_time = time.time()
    started_at = datetime.utcnow().isoformat()

    deepseek_client = await get_deepseek_client()
    step_logger = await get_step_logger()

    steps_log: list[StepLog] = []
    total_tokens = 0

    # Storage for intermediate results
    intermediate_results = {}

    try:
        # =====================================================================
        # B1: Validate and Enrich Profile
        # =====================================================================
        logger.info(f"[{track_id}] Starting B1: Validation")
        step_start = time.time()
        llm_calls_b1 = []

        try:
            b1_result, b1_meta = await b1_validate.run_b1_validate(
                profile, deepseek_client
            )
            b1_duration = time.time() - step_start
            b1_tokens = b1_meta["tokens_used"]
            total_tokens += b1_tokens

            llm_calls_b1.append(b1_meta)
            intermediate_results["validated_profile"] = b1_result.model_dump()

            # Log step
            await step_logger.log_step(
                track_id=track_id,
                step_name="B1_validate",
                step_output=b1_result.model_dump(),
                llm_calls=llm_calls_b1,
                duration_sec=b1_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B1_validate",
                    duration_sec=b1_duration,
                    tokens_used=b1_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B1 failed: {e}")
            raise PipelineError("B1_validate", str(e))

        # =====================================================================
        # B2: Formulate Competencies
        # =====================================================================
        logger.info(f"[{track_id}] Starting B2: Competencies")
        step_start = time.time()
        llm_calls_b2 = []

        try:
            b2_result, b2_meta = await b2_competencies.run_b2_competencies(
                intermediate_results["validated_profile"], deepseek_client
            )
            b2_duration = time.time() - step_start
            b2_tokens = b2_meta["tokens_used"]
            total_tokens += b2_tokens

            llm_calls_b2.append(b2_meta)
            intermediate_results["competency_set"] = b2_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B2_competencies",
                step_output=b2_result.model_dump(),
                llm_calls=llm_calls_b2,
                duration_sec=b2_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B2_competencies",
                    duration_sec=b2_duration,
                    tokens_used=b2_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B2 failed: {e}")
            raise PipelineError("B2_competencies", str(e))

        # =====================================================================
        # B3: KSA Matrix
        # =====================================================================
        logger.info(f"[{track_id}] Starting B3: KSA Matrix")
        step_start = time.time()
        llm_calls_b3 = []

        try:
            b3_result, b3_meta = await b3_ksa_matrix.run_b3_ksa_matrix(
                profile,
                intermediate_results["competency_set"],
                deepseek_client,
            )
            b3_duration = time.time() - step_start
            b3_tokens = b3_meta["tokens_used"]
            total_tokens += b3_tokens

            llm_calls_b3.append(b3_meta)
            intermediate_results["ksa_matrix"] = b3_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B3_ksa_matrix",
                step_output=b3_result.model_dump(),
                llm_calls=llm_calls_b3,
                duration_sec=b3_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B3_ksa_matrix",
                    duration_sec=b3_duration,
                    tokens_used=b3_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B3 failed: {e}")
            raise PipelineError("B3_ksa_matrix", str(e))

        # =====================================================================
        # B4: Learning Units
        # =====================================================================
        logger.info(f"[{track_id}] Starting B4: Learning Units")
        step_start = time.time()
        llm_calls_b4 = []

        try:
            b4_result, b4_meta = await b4_learning_units.run_b4_learning_units(
                intermediate_results["ksa_matrix"], deepseek_client
            )
            b4_duration = time.time() - step_start
            b4_tokens = b4_meta["tokens_used"]
            total_tokens += b4_tokens

            llm_calls_b4.append(b4_meta)
            intermediate_results["learning_units"] = b4_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B4_learning_units",
                step_output=b4_result.model_dump(),
                llm_calls=llm_calls_b4,
                duration_sec=b4_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B4_learning_units",
                    duration_sec=b4_duration,
                    tokens_used=b4_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B4 failed: {e}")
            raise PipelineError("B4_learning_units", str(e))

        # =====================================================================
        # B5: Hierarchy
        # =====================================================================
        logger.info(f"[{track_id}] Starting B5: Hierarchy")
        step_start = time.time()
        llm_calls_b5 = []

        try:
            b5_result, b5_meta = await b5_hierarchy.run_b5_hierarchy(
                intermediate_results["learning_units"],
                b1_result.total_time_budget_minutes,
                b1_result.estimated_weeks,
                deepseek_client,
            )
            b5_duration = time.time() - step_start
            b5_tokens = b5_meta["tokens_used"]
            total_tokens += b5_tokens

            llm_calls_b5.append(b5_meta)
            intermediate_results["hierarchy"] = b5_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B5_hierarchy",
                step_output=b5_result.model_dump(),
                llm_calls=llm_calls_b5,
                duration_sec=b5_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B5_hierarchy",
                    duration_sec=b5_duration,
                    tokens_used=b5_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B5 failed: {e}")
            raise PipelineError("B5_hierarchy", str(e))

        # =====================================================================
        # B6: Problem Formulations
        # =====================================================================
        logger.info(f"[{track_id}] Starting B6: Problem Formulations")
        step_start = time.time()
        llm_calls_b6 = []

        try:
            b6_result, b6_meta = await b6_problem_formulations.run_b6_problem_formulations(
                intermediate_results["learning_units"]["clusters"],
                intermediate_results["learning_units"],
                deepseek_client,
            )
            b6_duration = time.time() - step_start
            b6_tokens = b6_meta["tokens_used"]
            total_tokens += b6_tokens

            llm_calls_b6.append(b6_meta)
            intermediate_results["lesson_blueprints"] = b6_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B6_problem_formulations",
                step_output=b6_result.model_dump(),
                llm_calls=llm_calls_b6,
                duration_sec=b6_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B6_problem_formulations",
                    duration_sec=b6_duration,
                    tokens_used=b6_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B6 failed: {e}")
            raise PipelineError("B6_problem_formulations", str(e))

        # =====================================================================
        # B7: Schedule
        # =====================================================================
        logger.info(f"[{track_id}] Starting B7: Schedule Assembly")
        step_start = time.time()
        llm_calls_b7 = []

        try:
            b7_result, b7_meta = await b7_schedule.run_b7_schedule(
                intermediate_results["hierarchy"],
                intermediate_results["lesson_blueprints"],
                profile,
                b5_result.total_weeks,
                deepseek_client,
            )
            b7_duration = time.time() - step_start
            b7_tokens = b7_meta["tokens_used"]
            total_tokens += b7_tokens

            llm_calls_b7.append(b7_meta)
            intermediate_results["schedule"] = b7_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B7_schedule",
                step_output=b7_result.model_dump(),
                llm_calls=llm_calls_b7,
                duration_sec=b7_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B7_schedule",
                    duration_sec=b7_duration,
                    tokens_used=b7_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B7 failed: {e}")
            raise PipelineError("B7_schedule", str(e))

        # =====================================================================
        # B8: Validation
        # =====================================================================
        logger.info(f"[{track_id}] Starting B8: Validation")
        step_start = time.time()
        llm_calls_b8 = []

        try:
            # Construct complete track for validation
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
            b8_duration = time.time() - step_start
            b8_tokens = b8_meta["tokens_used"]
            total_tokens += b8_tokens

            llm_calls_b8.append(b8_meta)
            intermediate_results["validation"] = b8_result.model_dump()

            await step_logger.log_step(
                track_id=track_id,
                step_name="B8_validation",
                step_output=b8_result.model_dump(),
                llm_calls=llm_calls_b8,
                duration_sec=b8_duration,
            )

            steps_log.append(
                StepLog(
                    step_name="B8_validation",
                    duration_sec=b8_duration,
                    tokens_used=b8_tokens,
                    success=True,
                )
            )

        except Exception as e:
            logger.error(f"B8 failed: {e}")
            raise PipelineError("B8_validation", str(e))

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

        # Construct PersonalizedTrack
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

        logger.info(
            f"[{track_id}] Pipeline complete in {total_duration:.1f}s, "
            f"{total_tokens} tokens"
        )

        return {
            "track_data": track_data,
            "generation_metadata": metadata.model_dump(),
            "validation_b8": intermediate_results["validation"],
            "algorithm_version": algorithm_version,
        }

    except PipelineError:
        raise
    except Exception as e:
        logger.error(f"Unexpected pipeline error: {e}")
        raise PipelineError("unknown", f"Unexpected error: {e}")
