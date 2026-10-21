"""
etl/report.py — Pipeline execution summary and reporting.

Produces a concise human-readable summary of the pipeline run including
processing statistics, validation results, and elapsed timing.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from etl.validate import ValidationResult, summarise_results

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Holds runtime statistics gathered during a pipeline execution."""

    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    raw_rows: int = 0
    cleaned_rows: int = 0
    product_rows: int = 0
    category_rows: int = 0

    db_row_counts: Dict[str, int] = field(default_factory=dict)
    csv_paths: Dict[str, Path] = field(default_factory=dict)

    raw_validation_results: List[ValidationResult] = field(default_factory=list)
    cleaned_validation_results: List[ValidationResult] = field(default_factory=list)
    db_validation_results: List[ValidationResult] = field(default_factory=list)
    reconciliation_results: List[ValidationResult] = field(default_factory=list)

    @property
    def elapsed_seconds(self) -> float:
        """Elapsed wall-clock seconds since pipeline start."""
        end = self.end_time if self.end_time else time.time()
        return round(end - self.start_time, 2)

    def all_results(self) -> List[ValidationResult]:
        return (
            self.raw_validation_results
            + self.cleaned_validation_results
            + self.db_validation_results
            + self.reconciliation_results
        )


def print_summary(stats: PipelineStats, *, verbose: bool = False) -> str:
    """Build and print a concise execution summary.

    Parameters
    ----------
    stats : PipelineStats
        Collected statistics from the pipeline run.
    verbose : bool
        If True, print each individual validation result.

    Returns
    -------
    str
        The formatted summary string (also printed to stdout/log).
    """
    all_results = stats.all_results()
    passed, warnings, errors = summarise_results(all_results)

    lines = [
        "",
        "=" * 70,
        "  RETAIL ETL PIPELINE — EXECUTION SUMMARY",
        "=" * 70,
        f"  Elapsed time          : {stats.elapsed_seconds:.2f} s",
        f"  Raw rows loaded       : {stats.raw_rows:,}",
        f"  Cleaned rows output   : {stats.cleaned_rows:,}",
        f"  Products summarised   : {stats.product_rows}",
        f"  Categories summarised : {stats.category_rows}",
        "",
        "  SQLite Row Counts:",
    ]
    for table, count in stats.db_row_counts.items():
        lines.append(f"    {table:<35}: {count:,}")

    lines += [
        "",
        "  Validation Summary:",
        f"    PASSED   : {passed}",
        f"    WARNINGS : {warnings}",
        f"    ERRORS   : {errors}",
    ]

    if verbose or warnings > 0 or errors > 0:
        lines.append("")
        lines.append("  Validation Detail:")
        for r in all_results:
            if not r.passed or verbose:
                icon = "✓" if r.passed else ("✗" if r.severity == "ERROR" else "⚠")
                lines.append(f"    [{r.severity:<7}] {icon} {r.rule_id}: {r.message}")

    lines += [
        "",
        "  Output Files:",
    ]
    for name, path in stats.csv_paths.items():
        lines.append(f"    {name:<30}: {path}")

    status = "COMPLETED SUCCESSFULLY" if errors == 0 else "COMPLETED WITH ERRORS"
    lines += [
        "",
        f"  Status: {status}",
        "=" * 70,
        "",
    ]

    summary = "\n".join(lines)
    print(summary)
    logger.info("[Report] Pipeline %s — elapsed: %.2fs, errors: %d, warnings: %d",
                status, stats.elapsed_seconds, errors, warnings)
    return summary
