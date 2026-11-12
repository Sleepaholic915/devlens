
"""Run reproducible DevLens evaluation cases."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from devlens.agent import investigate


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.json"
RESULTS_DIR = ROOT / "evals" / "results"


def run_evaluations(case_id=None):
    load_dotenv(ROOT / ".env")

    cases = json.loads(
        CASES_PATH.read_text(encoding="utf-8")
    )

    if case_id is not None:
        cases = [
            case for case in cases
            if case["id"] == case_id
        ]

        if not cases:
            raise ValueError(f"Unknown case: {case_id}")

    results = []

    for case in cases:
        print(f"\nRunning: {case['id']}")

        try:
            report, trace = investigate(
                failure_description=case["failure"],
                repo_root=str(ROOT / case["repo"]),
            )

            results.append({
                "case_id": case["id"],
                "status": "completed",
                "report": report.model_dump(),
                "trace": trace,
                "tool_calls": len(trace),
            })

            print(f"Completed: {len(trace)} tool calls")

        except Exception as exc:
            results.append({
                "case_id": case["id"],
                "status": "error",
                "error": str(exc),
            })

            print(f"Failed: {exc}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output_path = RESULTS_DIR / f"run_{timestamp}.json"

    output_path.write_text(
        json.dumps(
            {
                "timestamp_utc": timestamp,
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved results to: {output_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        default=None,
        help="Run only the specified evaluation case",
    )
    args = parser.parse_args()

    run_evaluations(case_id=args.case)
