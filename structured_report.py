
import os

from dotenv import load_dotenv
from openai import OpenAI

from devlens.models import InvestigationReport
from devlens.validation import validate_report


load_dotenv()
client = OpenAI()

failure = """
Endpoint: GET /api/users/123
Expected status: 200
Actual status: 500
Response body:
{"error": "Internal Server Error"}
"""

response = client.responses.parse(
    model=os.environ["OPENAI_MODEL"],
    instructions=(
        "You are a backend debugging assistant. "
        "Separate observed facts from possible causes. "
        "Never claim an unverified root cause is confirmed. "
        "If there is insufficient evidence, hypotheses may be empty."
    ),
    input=f"Analyze this API failure:\n\n{failure}",
    text_format=InvestigationReport,
    max_output_tokens=1000,
)

# Response validation
print("Response status:", response.status)

if response.status != "completed":
    print("Incomplete details:", response.incomplete_details)
    raise SystemExit(1)

report = response.output_parsed

if report is None:
    print("No parsed report was returned.")
    raise SystemExit(1)

errors = validate_report(report)

if errors:
    print("Business validation failed:")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print("\n=== Investigation Report ===")
print(report.model_dump_json(indent=2))

print("\n=== Python Object ===")
print("Type:", type(report))
print("First observation:", report.observations[0] if report.observations else "None")
print("Hypotheses:", report.hypotheses)
print("Next steps:", report.next_steps)

if response.usage is not None:
    print("\n=== Token Usage ===")
    print("Input:", response.usage.input_tokens)
    print("Output:", response.usage.output_tokens)
    print("Total:", response.usage.total_tokens)
