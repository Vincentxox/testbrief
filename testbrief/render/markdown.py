"""Markdown renderer."""

from __future__ import annotations

from typing import List

from testbrief.models import Report, Status

MAX_MESSAGE_LENGTH = 200


def _cell(text: str) -> str:
    """Make text safe to place inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def _shorten(text: str, limit: int = MAX_MESSAGE_LENGTH) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _format_duration(seconds) -> str:
    return "n/a" if seconds is None else f"{seconds:.2f}s"


def _render_report(report: Report, top_slowest: int) -> List[str]:
    verdict = "FAIL" if report.has_failures else "PASS"
    lines = [
        f"## {report.source} [{verdict}]",
        "",
        f"Format: {report.tool}",
        "",
        "| Total | Passed | Failed | Errors | Skipped | Pass rate | Duration |",
        "|------:|-------:|-------:|-------:|--------:|----------:|---------:|",
        (
            f"| {report.total} | {report.passed} | {report.failed} "
            f"| {report.errors} | {report.skipped} "
            f"| {report.pass_rate:.1f}% | {_format_duration(report.duration)} |"
        ),
        "",
    ]

    problems = [c for c in report.cases if c.status in (Status.FAILED, Status.ERROR)]
    if problems:
        lines += [
            "### Failures",
            "",
            "| Test | Suite | Status | Message |",
            "|------|-------|--------|---------|",
        ]
        for case in problems:
            lines.append(
                f"| {_cell(case.name)} | {_cell(case.suite)} "
                f"| {case.status.value} | {_cell(_shorten(case.message))} |"
            )
        lines.append("")

    timed = [c for c in report.cases if c.duration is not None]
    if top_slowest > 0 and timed:
        slowest = sorted(timed, key=lambda c: c.duration, reverse=True)[:top_slowest]
        lines += [
            f"### Slowest {len(slowest)} tests",
            "",
            "| Test | Suite | Duration |",
            "|------|-------|---------:|",
        ]
        for case in slowest:
            lines.append(
                f"| {_cell(case.name)} | {_cell(case.suite)} "
                f"| {_format_duration(case.duration)} |"
            )
        lines.append("")

    return lines


def render_markdown(reports: List[Report], top_slowest: int = 5) -> str:
    failing = sum(1 for r in reports if r.has_failures)
    total = sum(r.total for r in reports)
    lines = [
        "# Test summary",
        "",
        f"{len(reports)} report(s), {total} test(s) in total. "
        + ("All reports are green." if failing == 0 else f"{failing} report(s) have failures."),
        "",
    ]
    for report in reports:
        lines += _render_report(report, top_slowest)
    return "\n".join(lines).rstrip() + "\n"
