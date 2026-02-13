"""Base classes for validation system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class ValidationSeverity(str, Enum):
    """Severity levels for validation checks."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationCheck:
    """Single validation check result."""

    check_id: str
    check_name: str
    category: Literal["schema", "reference", "graph", "business"]
    step: str
    passed: bool
    severity: ValidationSeverity
    message: str
    expected: Any | None = None
    actual: Any | None = None
    recommendation: str | None = None

    def __str__(self) -> str:
        """String representation for console output."""
        status = "✓" if self.passed else "✗"
        return f"{status} {self.step}: {self.check_name} - {self.message}"


@dataclass
class ValidationReport:
    """Complete validation report."""

    track_id: str | None
    timestamp: str
    mode: str
    steps_validated: list[str]
    total_checks: int
    passed_checks: int
    failed_checks: int
    checks: list[ValidationCheck] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    @property
    def critical_failures(self) -> list[ValidationCheck]:
        """Get all critical failures."""
        return [
            check
            for check in self.checks
            if not check.passed and check.severity == ValidationSeverity.CRITICAL
        ]

    @property
    def warnings(self) -> list[ValidationCheck]:
        """Get all warnings."""
        return [
            check
            for check in self.checks
            if not check.passed and check.severity == ValidationSeverity.WARNING
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "track_id": self.track_id,
            "timestamp": self.timestamp,
            "mode": self.mode,
            "steps_validated": self.steps_validated,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "success_rate": self.success_rate,
            "checks": [
                {
                    "check_id": check.check_id,
                    "check_name": check.check_name,
                    "category": check.category,
                    "step": check.step,
                    "passed": check.passed,
                    "severity": check.severity.value,
                    "message": check.message,
                    "expected": check.expected,
                    "actual": check.actual,
                    "recommendation": check.recommendation,
                }
                for check in self.checks
            ],
            "summary": self.summary,
        }

    @classmethod
    def create(
        cls,
        track_id: str | None,
        mode: str,
        steps_validated: list[str],
        checks: list[ValidationCheck],
    ) -> "ValidationReport":
        """Create validation report from checks."""
        passed = sum(1 for check in checks if check.passed)
        failed = sum(1 for check in checks if not check.passed)

        # Generate summary
        summary = {
            "critical_failures": len([c for c in checks if not c.passed and c.severity == ValidationSeverity.CRITICAL]),
            "warnings": len([c for c in checks if not c.passed and c.severity == ValidationSeverity.WARNING]),
            "by_category": {},
            "by_step": {},
        }

        # Group by category
        for check in checks:
            if check.category not in summary["by_category"]:
                summary["by_category"][check.category] = {"passed": 0, "failed": 0}
            if check.passed:
                summary["by_category"][check.category]["passed"] += 1
            else:
                summary["by_category"][check.category]["failed"] += 1

        # Group by step
        for check in checks:
            if check.step not in summary["by_step"]:
                summary["by_step"][check.step] = {"passed": 0, "failed": 0}
            if check.passed:
                summary["by_step"][check.step]["passed"] += 1
            else:
                summary["by_step"][check.step]["failed"] += 1

        return cls(
            track_id=track_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            mode=mode,
            steps_validated=steps_validated,
            total_checks=len(checks),
            passed_checks=passed,
            failed_checks=failed,
            checks=checks,
            summary=summary,
        )
