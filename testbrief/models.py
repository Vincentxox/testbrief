"""Data model shared by every parser and renderer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Status(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class CaseResult:
    """The outcome of a single test case or assertion."""

    name: str
    suite: str = ""
    status: Status = Status.PASSED
    duration: Optional[float] = None  # seconds, when the report provides it
    message: str = ""


@dataclass
class Report:
    """All results that came from one input file."""

    source: str
    tool: str
    cases: List[CaseResult] = field(default_factory=list)

    def _count(self, status: Status) -> int:
        return sum(1 for case in self.cases if case.status == status)

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return self._count(Status.PASSED)

    @property
    def failed(self) -> int:
        return self._count(Status.FAILED)

    @property
    def errors(self) -> int:
        return self._count(Status.ERROR)

    @property
    def skipped(self) -> int:
        return self._count(Status.SKIPPED)

    @property
    def has_failures(self) -> bool:
        return self.failed + self.errors > 0

    @property
    def pass_rate(self) -> float:
        """Share of executed (non-skipped) tests that passed, from 0 to 100."""
        executed = self.total - self.skipped
        if executed == 0:
            return 0.0
        return 100.0 * self.passed / executed

    @property
    def duration(self) -> Optional[float]:
        durations = [c.duration for c in self.cases if c.duration is not None]
        return sum(durations) if durations else None
