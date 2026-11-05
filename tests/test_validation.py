
from devlens.models import InvestigationReport
from devlens.validation import validate_report


def test_valid_report():
    report = InvestigationReport(
        observations=["HTTP 500"],
        hypotheses=["Possible server exception"],
        next_steps=["Inspect logs"],
    )

    assert validate_report(report) == []


def test_empty_hypotheses_allowed():
    report = InvestigationReport(
        observations=["HTTP 500"],
        hypotheses=[],
        next_steps=["Inspect logs"],
    )

    assert validate_report(report) == []


def test_empty_observations_rejected():
    report = InvestigationReport(
        observations=[],
        hypotheses=[],
        next_steps=["Inspect logs"],
    )

    errors = validate_report(report)

    assert "At least one observation is required." in errors


def test_empty_next_steps_rejected():
    report = InvestigationReport(
        observations=["HTTP 500"],
        hypotheses=[],
        next_steps=[],
    )

    errors = validate_report(report)

    assert "At least one next step is required." in errors


def test_both_required_fields_empty():
    report = InvestigationReport(
        observations=[],
        hypotheses=[],
        next_steps=[],
    )

    assert len(validate_report(report)) == 2
