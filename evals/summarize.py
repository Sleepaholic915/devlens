
"""Summarize a saved DevLens evaluation run."""

import argparse
import json
from pathlib import Path

from devlens.models import InvestigationReport
from devlens.validation import validate_report


def summarize(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data["results"]

    total = len(results)
    completed = 0
    valid_reports = 0
    tool_calls = 0
    successful_tools = 0

    for case in results:
        if case["status"] != "completed":
            continue

        completed += 1

        report = InvestigationReport.model_validate(
            case["report"]
        )

        if not validate_report(report):
            valid_reports += 1

        trace = case["trace"]
        tool_calls += len(trace)

        successful_tools += sum(
            item["ok"] is True for item in trace
        )

    def rate(numerator, denominator):
        return numerator / denominator if denominator else 0.0

    summary = {
        "total_cases": total,
        "completed_cases": completed,
        "completion_rate": rate(completed, total),
        "report_validity_rate": rate(valid_reports, total),
        "tool_success_rate": rate(successful_tools, tool_calls),
        "average_tool_calls": rate(tool_calls, total),
    }

    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("result_file", type=Path)
    args = parser.parse_args()

    summarize(args.result_file)
