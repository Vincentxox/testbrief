"""Parser for Newman (Postman CLI) JSON reports.

Generate one with:  newman run collection.json -r json --reporter-json-export out.json
Every assertion becomes one test case, grouped by the request it belongs to.
"""

from __future__ import annotations

import json

from testbrief.models import CaseResult, Report, Status


def parse_newman(path: str) -> Report:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)

    run = data.get("run") if isinstance(data, dict) else None
    if not isinstance(run, dict) or not isinstance(run.get("executions"), list):
        raise ValueError(f"{path}: not a Newman JSON report (missing run.executions)")

    report = Report(source=path, tool="Newman JSON")
    for execution in run["executions"]:
        request_name = (execution.get("item") or {}).get("name", "unnamed request")
        assertions = execution.get("assertions") or []
        request_error = execution.get("requestError")

        if request_error and not assertions:
            report.cases.append(
                CaseResult(
                    name=request_name,
                    suite=request_name,
                    status=Status.ERROR,
                    message=str(request_error.get("message", request_error)),
                )
            )
            continue

        for assertion in assertions:
            error = assertion.get("error")
            if assertion.get("skipped"):
                status, message = Status.SKIPPED, ""
            elif error:
                status = Status.FAILED
                message = " ".join(
                    str(error.get("message") or error.get("name") or "").split()
                )
            else:
                status, message = Status.PASSED, ""

            report.cases.append(
                CaseResult(
                    name=assertion.get("assertion", "unnamed assertion"),
                    suite=request_name,
                    status=status,
                    message=message,
                )
            )
    return report
