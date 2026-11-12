
import json

from evals.summarize import summarize


def test_summary_metrics(tmp_path):
    data = {
        "results": [
            {
                "status": "completed",
                "report": {
                    "observations": ["Found missing check"],
                    "hypotheses": [],
                    "next_steps": ["Add validation"],
                },
                "trace": [
                    {"ok": True},
                    {"ok": False},
                ],
            },
            {
                "status": "error",
                "error": "Investigation failed",
            },
        ]
    }

    path = tmp_path / "results.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    result = summarize(path)

    assert result["total_cases"] == 2
    assert result["completed_cases"] == 1
    assert result["completion_rate"] == 0.5
    assert result["report_validity_rate"] == 0.5
    assert result["tool_success_rate"] == 0.5
    assert result["average_tool_calls"] == 1.0


def test_empty_evaluation(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text(
        json.dumps({"results": []}),
        encoding="utf-8",
    )

    result = summarize(path)

    assert result["total_cases"] == 0
    assert result["completion_rate"] == 0.0
    assert result["tool_success_rate"] == 0.0
    assert result["average_tool_calls"] == 0.0
