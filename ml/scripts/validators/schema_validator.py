"""Schema validator for Pydantic model validation."""

from typing import Any

from pydantic import ValidationError

from ml.src.schemas.pipeline_steps import (
    BlueprintsOutput,
    CompetencySet,
    HierarchyOutput,
    KSAMatrix,
    LearningUnitsOutput,
    ScheduleOutput,
    ValidatedStudentProfile,
    ValidationResult,
)

from .base import ValidationCheck, ValidationSeverity

# Mapping of step names to Pydantic schemas
SCHEMA_MAP = {
    "B1_validate": ValidatedStudentProfile,
    "B2_competencies": CompetencySet,
    "B3_ksa_matrix": KSAMatrix,
    "B4_learning_units": LearningUnitsOutput,
    "B5_hierarchy": HierarchyOutput,
    "B6_problem_formulations": BlueprintsOutput,
    "B7_schedule": ScheduleOutput,
    "B8_validation": ValidationResult,
}


class SchemaValidator:
    """Validates pipeline step outputs against Pydantic schemas."""

    def validate_step(self, step_name: str, step_data: dict[str, Any]) -> list[ValidationCheck]:
        """
        Validate a single step output against its schema.

        Args:
            step_name: Name of the step (e.g., "B1_validate")
            step_data: Step output data to validate

        Returns:
            List of validation checks
        """
        checks = []

        # Get schema for this step
        schema = SCHEMA_MAP.get(step_name)
        if not schema:
            checks.append(
                ValidationCheck(
                    check_id=f"{step_name}_schema_unknown",
                    check_name="Schema Definition",
                    category="schema",
                    step=step_name,
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"No schema defined for step {step_name}",
                    recommendation=f"Add {step_name} schema to SCHEMA_MAP",
                )
            )
            return checks

        # Try to validate against schema
        try:
            schema(**step_data)
            checks.append(
                ValidationCheck(
                    check_id=f"{step_name}_schema_valid",
                    check_name="Pydantic Schema Validation",
                    category="schema",
                    step=step_name,
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"Step output matches {schema.__name__} schema",
                )
            )
        except ValidationError as e:
            # Parse Pydantic errors
            for error in e.errors():
                field_path = " → ".join(str(loc) for loc in error["loc"])
                error_msg = error["msg"]
                error_type = error["type"]

                checks.append(
                    ValidationCheck(
                        check_id=f"{step_name}_schema_error_{field_path}",
                        check_name="Schema Field Validation",
                        category="schema",
                        step=step_name,
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Field '{field_path}': {error_msg} (type: {error_type})",
                        expected=error.get("ctx"),
                        actual=error.get("input"),
                        recommendation=f"Fix field '{field_path}' in step output or update schema",
                    )
                )
        except Exception as e:
            checks.append(
                ValidationCheck(
                    check_id=f"{step_name}_schema_exception",
                    check_name="Schema Validation Error",
                    category="schema",
                    step=step_name,
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Unexpected error during validation: {str(e)}",
                    recommendation="Check step output data format",
                )
            )

        return checks

    def validate_all_steps(
        self, steps_data: dict[str, dict[str, Any]]
    ) -> list[ValidationCheck]:
        """
        Validate all steps.

        Args:
            steps_data: Dictionary mapping step names to their output data

        Returns:
            List of all validation checks
        """
        all_checks = []
        for step_name, step_output in steps_data.items():
            checks = self.validate_step(step_name, step_output)
            all_checks.extend(checks)
        return all_checks
