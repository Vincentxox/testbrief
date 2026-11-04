"""Parser for JUnit-style XML reports (JUnit, TestNG, pytest, Jenkins, ...)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Optional

from testbrief.models import CaseResult, Report, Status


def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _message(node: ET.Element) -> str:
    text = node.get("message") or (node.text or "")
    return " ".join(text.split())


def parse_junit(path: str) -> Report:
    root = ET.parse(path).getroot()
    if root.tag not in ("testsuite", "testsuites"):
        raise ValueError(
            f"{path}: not a JUnit XML report (root element is <{root.tag}>)"
        )

    report = Report(source=path, tool="JUnit XML")
    # iter() yields the root itself when it is a <testsuite>, and every nested
    # <testsuite> below it. Test cases are always direct children of a suite,
    # so nothing is counted twice.
    for suite in root.iter("testsuite"):
        suite_name = suite.get("name", "")
        for case in suite.findall("testcase"):
            status = Status.PASSED
            message = ""
            for child_tag, child_status in (
                ("failure", Status.FAILED),
                ("error", Status.ERROR),
                ("skipped", Status.SKIPPED),
            ):
                child = case.find(child_tag)
                if child is not None:
                    status = child_status
                    message = _message(child)
                    break

            classname = case.get("classname", "")
            report.cases.append(
                CaseResult(
                    name=case.get("name", "unnamed test"),
                    suite=classname or suite_name,
                    status=status,
                    duration=_to_float(case.get("time")),
                    message=message,
                )
            )
    return report
