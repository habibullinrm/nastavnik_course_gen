"""Report generator for validation results."""

import json
from pathlib import Path
from typing import TextIO

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from .base import ValidationReport, ValidationSeverity


class ReportGenerator:
    """Generates validation reports in various formats."""

    def __init__(self):
        self.console = Console()

    def print_console(self, report: ValidationReport) -> None:
        """
        Print validation report to console with Rich formatting.

        Args:
            report: Validation report to print
        """
        # Header
        header_text = "ML Pipeline Validation Report"
        meta_info = f"Track ID: {report.track_id or 'N/A'} | Mode: {report.mode} | Steps: {len(report.steps_validated)}"

        self.console.print()
        self.console.print(
            Panel(
                f"[bold cyan]{header_text}[/bold cyan]\n{meta_info}",
                expand=False,
            )
        )
        self.console.print()

        # Summary by category
        self._print_category_summary(report)

        # Summary by step
        self._print_step_summary(report)

        # Failed checks details
        if report.failed_checks > 0:
            self._print_failed_checks(report)

        # Overall summary
        self._print_overall_summary(report)

        # Critical issues and recommendations
        if report.critical_failures:
            self._print_critical_issues(report)

    def _print_category_summary(self, report: ValidationReport) -> None:
        """Print summary by validation category."""
        self.console.print("[bold]Validation by Category:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Passed", style="green")
        table.add_column("Failed", style="red")
        table.add_column("Success Rate", justify="right")

        for category, stats in report.summary.get("by_category", {}).items():
            passed = stats["passed"]
            failed = stats["failed"]
            total = passed + failed
            success_rate = (passed / total * 100) if total > 0 else 0

            # Color code the success rate
            if success_rate == 100:
                rate_style = "green"
            elif success_rate >= 80:
                rate_style = "yellow"
            else:
                rate_style = "red"

            table.add_row(
                category.capitalize(),
                str(passed),
                str(failed),
                f"[{rate_style}]{success_rate:.1f}%[/{rate_style}]",
            )

        self.console.print(table)
        self.console.print()

    def _print_step_summary(self, report: ValidationReport) -> None:
        """Print summary by pipeline step."""
        self.console.print("[bold]Validation by Step:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Step", style="cyan")
        table.add_column("Passed", style="green")
        table.add_column("Failed", style="red")
        table.add_column("Status")

        for step, stats in report.summary.get("by_step", {}).items():
            passed = stats["passed"]
            failed = stats["failed"]

            if failed == 0:
                status = Text("✓ OK", style="green")
            else:
                status = Text("✗ FAILED", style="red")

            table.add_row(step, str(passed), str(failed), status)

        self.console.print(table)
        self.console.print()

    def _print_failed_checks(self, report: ValidationReport) -> None:
        """Print details of failed checks."""
        self.console.print("[bold red]Failed Checks:[/bold red]")

        for check in report.checks:
            if not check.passed:
                severity_color = {
                    ValidationSeverity.CRITICAL: "red",
                    ValidationSeverity.WARNING: "yellow",
                    ValidationSeverity.INFO: "blue",
                }[check.severity]

                self.console.print(
                    f"  [{severity_color}]✗[/{severity_color}] "
                    f"[bold]{check.step}[/bold]: {check.check_name}"
                )
                self.console.print(f"     {check.message}")

                if check.expected:
                    self.console.print(f"     Expected: {check.expected}")
                if check.actual:
                    self.console.print(f"     Actual: {check.actual}")
                if check.recommendation:
                    self.console.print(
                        f"     [cyan]💡 Recommendation:[/cyan] {check.recommendation}"
                    )
                self.console.print()

    def _print_overall_summary(self, report: ValidationReport) -> None:
        """Print overall validation summary."""
        self.console.print("═" * 70)
        self.console.print()

        # Success rate with color
        success_rate = report.success_rate
        if success_rate == 100:
            rate_style = "bold green"
        elif success_rate >= 80:
            rate_style = "bold yellow"
        else:
            rate_style = "bold red"

        self.console.print(
            f"[bold]Summary:[/bold] "
            f"[green]{report.passed_checks} passed[/green]  "
            f"[red]{report.failed_checks} failed[/red]  "
            f"[{rate_style}]{success_rate:.1f}% success rate[/{rate_style}]"
        )
        self.console.print()

    def _print_critical_issues(self, report: ValidationReport) -> None:
        """Print critical issues and recommendations."""
        critical = report.critical_failures
        warnings = report.warnings

        if critical:
            self.console.print(f"[bold red]Critical Issues: {len(critical)}[/bold red]")
            for i, check in enumerate(critical[:5], 1):  # Show first 5
                self.console.print(f"  {i}. {check.step}: {check.message}")
            if len(critical) > 5:
                self.console.print(f"  ... and {len(critical) - 5} more")
            self.console.print()

        if warnings:
            self.console.print(f"[bold yellow]Warnings: {len(warnings)}[/bold yellow]")
            for i, check in enumerate(warnings[:3], 1):  # Show first 3
                self.console.print(f"  {i}. {check.step}: {check.message}")
            if len(warnings) > 3:
                self.console.print(f"  ... and {len(warnings) - 3} more")
            self.console.print()

        # Actionable recommendations
        recommendations = [
            check.recommendation
            for check in report.critical_failures
            if check.recommendation
        ]
        if recommendations:
            self.console.print("[bold cyan]Recommendations:[/bold cyan]")
            for rec in recommendations[:5]:  # Show first 5
                self.console.print(f"  • {rec}")
            self.console.print()

    def save_json(self, report: ValidationReport, output_file: Path) -> None:
        """
        Save validation report as JSON.

        Args:
            report: Validation report to save
            output_file: Path to output JSON file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        self.console.print(f"[green]Report saved to {output_file}[/green]")

    def save_text(self, report: ValidationReport, output_file: Path) -> None:
        """
        Save validation report as plain text.

        Args:
            report: Validation report to save
            output_file: Path to output text file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("ML Pipeline Validation Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Track ID: {report.track_id or 'N/A'}\n")
            f.write(f"Mode: {report.mode}\n")
            f.write(f"Timestamp: {report.timestamp}\n")
            f.write(f"Steps Validated: {', '.join(report.steps_validated)}\n\n")

            f.write(f"Total Checks: {report.total_checks}\n")
            f.write(f"Passed: {report.passed_checks}\n")
            f.write(f"Failed: {report.failed_checks}\n")
            f.write(f"Success Rate: {report.success_rate:.1f}%\n\n")

            if report.failed_checks > 0:
                f.write("Failed Checks:\n")
                f.write("-" * 70 + "\n")
                for check in report.checks:
                    if not check.passed:
                        f.write(f"\n✗ {check.step}: {check.check_name}\n")
                        f.write(f"  Message: {check.message}\n")
                        if check.recommendation:
                            f.write(f"  Recommendation: {check.recommendation}\n")

        self.console.print(f"[green]Report saved to {output_file}[/green]")
