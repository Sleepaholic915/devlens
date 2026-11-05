from devlens.models import InvestigationReport


def validate_report(report: InvestigationReport) -> list[str]:
    """Return business-rule violations; [] means all checks passed."""
    errors = []

    if not report.observations:
        errors.append("At least one observation is required.")

    if not report.next_steps:
        errors.append("At least one next step is required.")

    return errors
