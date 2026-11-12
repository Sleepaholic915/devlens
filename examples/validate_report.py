from devlens.models import InvestigationReport


def validate_report(report: InvestigationReport) -> list[str]:
    """Return business-rule violations, or [] if all checks pass."""
    errors = []

    if not report.observations:
        errors.append("At least one observation is required.")

    if not report.next_steps:
        errors.append("At least one next step is required.")

    return errors


# Case 1: Valid
valid_report = InvestigationReport(
    observations=["GET /api/users/123 returned HTTP 500"],
    hypotheses=[],
    next_steps=["Inspect server logs"],
)

# Case 2: Invalid business rules, but valid Pydantic types
invalid_report = InvestigationReport(
    observations=[],
    hypotheses=["Database error"],
    next_steps=[],
)

print("Case 1:", validate_report(valid_report))
print("Case 2:", validate_report(invalid_report))
