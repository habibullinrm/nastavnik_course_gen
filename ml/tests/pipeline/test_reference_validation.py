"""Tests for reference validator."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import pytest

from validators.base import ValidationSeverity
from validators.reference_validator import ReferenceValidator


def test_reference_validator_b3_internal_valid(valid_b3_output):
    """Test B3 internal reference validation with valid data."""
    validator = ReferenceValidator()
    checks = validator.validate_b3_internal(valid_b3_output)

    # All references should be valid
    assert all(c.passed for c in checks)
    assert len(checks) > 0


def test_reference_validator_b3_internal_invalid(invalid_b3_output):
    """Test B3 internal reference validation with invalid data."""
    validator = ReferenceValidator()
    checks = validator.validate_b3_internal(invalid_b3_output)

    # Should have failed checks for broken references
    failed_checks = [c for c in checks if not c.passed]
    assert len(failed_checks) > 0

    # Check that specific broken references are detected
    messages = [c.message for c in failed_checks]
    assert any("k999" in msg for msg in messages)
    assert any("s999" in msg for msg in messages)


def test_reference_validator_b2_to_b3(valid_b2_output, valid_b3_output):
    """Test B2→B3 reference validation."""
    validator = ReferenceValidator()
    checks = validator.validate_b2_to_b3(valid_b2_output, valid_b3_output)

    assert len(checks) > 0
    # Should have at least one check for comp_1


def test_reference_validator_b4_to_b5_valid(valid_b4_output, valid_b5_output):
    """Test B4→B5 reference validation with valid data."""
    validator = ReferenceValidator()
    checks = validator.validate_b4_to_b5(valid_b4_output, valid_b5_output)

    # All unit IDs in sequence should exist in B4
    failed_checks = [c for c in checks if not c.passed]
    assert len(failed_checks) == 0


def test_reference_validator_b4_to_b5_invalid(valid_b4_output, invalid_b5_output):
    """Test B4→B5 reference validation with invalid data."""
    validator = ReferenceValidator()
    checks = validator.validate_b4_to_b5(valid_b4_output, invalid_b5_output)

    # Should detect unknown unit ID pu999
    failed_checks = [c for c in checks if not c.passed]
    assert len(failed_checks) > 0
    assert any("pu999" in c.message for c in failed_checks)


def test_reference_validator_all(
    valid_b2_output, valid_b3_output, valid_b4_output, valid_b5_output
):
    """Test validation of all reference checks."""
    validator = ReferenceValidator()
    steps_data = {
        "B2_competencies": valid_b2_output,
        "B3_ksa_matrix": valid_b3_output,
        "B4_learning_units": valid_b4_output,
        "B5_hierarchy": valid_b5_output,
    }

    checks = validator.validate_all(steps_data)

    assert len(checks) > 0
    # Most checks should pass with valid data
    passed_checks = [c for c in checks if c.passed]
    failed_checks = [c for c in checks if not c.passed]

    # Allow some warnings, but no critical failures
    critical_failures = [
        c for c in failed_checks if c.severity == ValidationSeverity.CRITICAL
    ]
    assert len(critical_failures) == 0
