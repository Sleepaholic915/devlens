from pydantic import ValidationError
from devlens.models import InvestigationReport


valid_report = {
    "observations": [
        "GET /api/users/123 returned HTTP 500"
    ],
    "hypotheses": [
        "Database connection failure",
        "Response serialization error",
    ],
    "next_steps": [
        "Inspect server logs",
    ],
}

report = InvestigationReport.model_validate(valid_report)

print("=== Valid Report ===")
print(report.model_dump_json(indent=2))


invalid_report = {
    "observations": [
        "GET /api/users/123 returned HTTP 500"
    ],
    "hypotheses": "Database connection failure",
    "next_steps": [
        "Inspect server logs",
    ],
}

print("\n=== Invalid Report ===")

try:
    InvestigationReport.model_validate(invalid_report)
except ValidationError as e:
    print(e)