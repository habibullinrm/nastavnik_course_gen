#!/usr/bin/env python3
"""CLI tool for validating ML pipeline outputs."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validators.base import ValidationReport
from validators.reference_validator import ReferenceValidator
from validators.report_generator import ReportGenerator
from validators.schema_validator import SchemaValidator


def load_step_logs(track_id: str, logs_dir: Path = None) -> dict[str, dict[str, Any]]:
    """
    Load all B1-B8 step logs for a track.

    Args:
        track_id: ID of the track to load
        logs_dir: Base directory for logs (defaults to ml/logs)

    Returns:
        Dictionary mapping step names to their step_output data
    """
    if logs_dir is None:
        # Default to ml/logs from script location
        script_dir = Path(__file__).parent.parent
        logs_dir = script_dir / "ml" / "logs"

    track_dir = logs_dir / track_id
    if not track_dir.exists():
        raise ValueError(f"Track directory not found: {track_dir}")

    steps_data = {}
    for step_file in sorted(track_dir.glob("step_*.json")):
        try:
            with open(step_file, encoding="utf-8") as f:
                log_data = json.load(f)
                step_name = log_data["step_name"]
                steps_data[step_name] = log_data["step_output"]
        except Exception as e:
            print(f"Warning: Failed to load {step_file}: {e}", file=sys.stderr)

    return steps_data


def load_mock_data(mock_file: Path) -> dict[str, dict[str, Any]]:
    """
    Load mock data from JSON file.

    Args:
        mock_file: Path to JSON file with mock step data

    Returns:
        Dictionary mapping step names to their data
    """
    if not mock_file.exists():
        raise ValueError(f"Mock data file not found: {mock_file}")

    with open(mock_file, encoding="utf-8") as f:
        return json.load(f)


def validate_logs_mode(
    track_id: str,
    steps: list[str] | None = None,
    verbose: bool = False,
    fail_fast: bool = False,
) -> ValidationReport:
    """
    Validate existing pipeline logs.

    Args:
        track_id: Track ID to validate
        steps: Optional list of steps to validate (e.g., ["B1_validate", "B2_competencies"])
        verbose: Enable verbose output
        fail_fast: Stop on first error

    Returns:
        ValidationReport
    """
    # Load logs
    if verbose:
        print(f"Loading logs for track {track_id}...")
    steps_data = load_step_logs(track_id)

    if not steps_data:
        raise ValueError(f"No step logs found for track {track_id}")

    # Filter steps if specified
    if steps:
        steps_data = {k: v for k, v in steps_data.items() if k in steps}

    if verbose:
        print(f"Loaded {len(steps_data)} steps: {list(steps_data.keys())}")

    # Run validators
    all_checks = []

    # Schema validation
    if verbose:
        print("\nRunning schema validation...")
    schema_validator = SchemaValidator()
    schema_checks = schema_validator.validate_all_steps(steps_data)
    all_checks.extend(schema_checks)

    if fail_fast and any(not check.passed for check in schema_checks):
        return ValidationReport.create(
            track_id=track_id,
            mode="logs",
            steps_validated=list(steps_data.keys()),
            checks=all_checks,
        )

    # Reference validation
    if verbose:
        print("Running reference validation...")
    reference_validator = ReferenceValidator()
    reference_checks = reference_validator.validate_all(steps_data)
    all_checks.extend(reference_checks)

    # Create report
    return ValidationReport.create(
        track_id=track_id,
        mode="logs",
        steps_validated=list(steps_data.keys()),
        checks=all_checks,
    )


def validate_mock_mode(
    mock_file: Path,
    steps: list[str] | None = None,
    verbose: bool = False,
    fail_fast: bool = False,
) -> ValidationReport:
    """
    Validate mock data.

    Args:
        mock_file: Path to mock data JSON file
        steps: Optional list of steps to validate
        verbose: Enable verbose output
        fail_fast: Stop on first error

    Returns:
        ValidationReport
    """
    # Load mock data
    if verbose:
        print(f"Loading mock data from {mock_file}...")
    steps_data = load_mock_data(mock_file)

    # Filter steps if specified
    if steps:
        steps_data = {k: v for k, v in steps_data.items() if k in steps}

    if verbose:
        print(f"Loaded {len(steps_data)} steps: {list(steps_data.keys())}")

    # Run validators
    all_checks = []

    # Schema validation
    if verbose:
        print("\nRunning schema validation...")
    schema_validator = SchemaValidator()
    schema_checks = schema_validator.validate_all_steps(steps_data)
    all_checks.extend(schema_checks)

    if fail_fast and any(not check.passed for check in schema_checks):
        return ValidationReport.create(
            track_id=None,
            mode="mock",
            steps_validated=list(steps_data.keys()),
            checks=all_checks,
        )

    # Reference validation
    if verbose:
        print("Running reference validation...")
    reference_validator = ReferenceValidator()
    reference_checks = reference_validator.validate_all(steps_data)
    all_checks.extend(reference_checks)

    # Create report
    return ValidationReport.create(
        track_id=None,
        mode="mock",
        steps_validated=list(steps_data.keys()),
        checks=all_checks,
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate ML pipeline outputs for data integrity and correctness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate existing logs
  python validate_pipeline.py --mode logs --track-id e30c05f4-1f18-4cc6-af2c-3b9b441c80fd

  # Validate with verbose output
  python validate_pipeline.py --mode logs --track-id <id> --verbose

  # Validate only specific steps
  python validate_pipeline.py --mode logs --track-id <id> --steps B1_validate,B2_competencies

  # Validate mock data
  python validate_pipeline.py --mode mock --mock-data tests/fixtures/test_data.json

  # Save report as JSON
  python validate_pipeline.py --mode logs --track-id <id> --output-format json --output-file report.json
        """,
    )

    # Main arguments
    parser.add_argument(
        "--mode",
        choices=["logs", "mock"],
        required=True,
        help="Validation mode: logs (existing track logs) or mock (test data)",
    )

    # Logs mode arguments
    parser.add_argument(
        "--track-id",
        help="Track ID to validate (required for logs mode)",
    )

    # Mock mode arguments
    parser.add_argument(
        "--mock-data",
        type=Path,
        help="Path to mock data JSON file (required for mock mode)",
    )

    # Optional filters
    parser.add_argument(
        "--steps",
        help="Comma-separated list of steps to validate (e.g., B1_validate,B2_competencies)",
    )

    # Output options
    parser.add_argument(
        "--output-format",
        choices=["console", "json", "text"],
        default="console",
        help="Output format (default: console)",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Output file path (required for json/text formats)",
    )

    # Behavior options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop validation on first critical error",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.mode == "logs" and not args.track_id:
        parser.error("--track-id is required for logs mode")
    if args.mode == "mock" and not args.mock_data:
        parser.error("--mock-data is required for mock mode")
    if args.output_format in ["json", "text"] and not args.output_file:
        parser.error(f"--output-file is required for {args.output_format} format")

    # Parse steps filter
    steps_filter = None
    if args.steps:
        steps_filter = [s.strip() for s in args.steps.split(",")]

    # Run validation
    try:
        if args.mode == "logs":
            report = validate_logs_mode(
                track_id=args.track_id,
                steps=steps_filter,
                verbose=args.verbose,
                fail_fast=args.fail_fast,
            )
        else:  # mock mode
            report = validate_mock_mode(
                mock_file=args.mock_data,
                steps=steps_filter,
                verbose=args.verbose,
                fail_fast=args.fail_fast,
            )

        # Generate report
        report_gen = ReportGenerator()

        if args.output_format == "console":
            report_gen.print_console(report)
        elif args.output_format == "json":
            report_gen.save_json(report, args.output_file)
        elif args.output_format == "text":
            report_gen.save_text(report, args.output_file)

        # Exit with appropriate code
        exit_code = 0 if report.failed_checks == 0 else 1
        if len(report.critical_failures) > 0:
            exit_code = 2

        sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
