"""Tests for schema validator."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest

from validators.base import ValidationSeverity
from validators.schema_validator import SchemaValidator


def test_schema_validator_valid_b1(valid_b1_output):
    """Test schema validation with valid B1 output."""
    validator = SchemaValidator()
    checks = validator.validate_step("B1_validate", valid_b1_output)

    assert len(checks) == 1
    assert checks[0].passed is True
    assert checks[0].category == "schema"
    assert checks[0].step == "B1_validate"


def test_schema_validator_invalid_b1(invalid_b1_output):
    """Test schema validation with invalid B1 output."""
    validator = SchemaValidator()
    checks = validator.validate_step("B1_validate", invalid_b1_output)

    # Should have multiple failed checks for missing fields
    failed_checks = [c for c in checks if not c.passed]
    assert len(failed_checks) > 0
    assert all(c.severity == ValidationSeverity.CRITICAL for c in failed_checks)


def test_schema_validator_valid_b2(valid_b2_output):
    """Test schema validation with valid B2 output."""
    validator = SchemaValidator()
    checks = validator.validate_step("B2_competencies", valid_b2_output)

    assert len(checks) == 1
    assert checks[0].passed is True


def test_schema_validator_valid_b3(valid_b3_output):
    """Test schema validation with valid B3 output."""
    validator = SchemaValidator()
    checks = validator.validate_step("B3_ksa_matrix", valid_b3_output)

    assert len(checks) == 1
    assert checks[0].passed is True


def test_schema_validator_unknown_step():
    """Test schema validation with unknown step name."""
    validator = SchemaValidator()
    checks = validator.validate_step("B99_unknown", {})

    assert len(checks) == 1
    assert checks[0].passed is False
    assert "No schema defined" in checks[0].message


def test_schema_validator_all_steps(
    valid_b1_output, valid_b2_output, valid_b3_output
):
    """Test validation of multiple steps."""
    validator = SchemaValidator()
    steps_data = {
        "B1_validate": valid_b1_output,
        "B2_competencies": valid_b2_output,
        "B3_ksa_matrix": valid_b3_output,
    }

    checks = validator.validate_all_steps(steps_data)

    assert len(checks) == 3
    assert all(c.passed for c in checks)
